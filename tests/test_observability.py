import json
import logging
import re
from time import time
from urllib.request import urlopen

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.agent import RetrievalError
from app.config import Settings
from app.dependencies import get_agent_service
from app.llm import (
    GenerationResult,
    GenerationStreamCompleted,
    GenerationStreamStarted,
    GenerationUsage,
)
from app.main import app, create_app
from app.models import ResponseCreateRequest
from app.observability import (
    HTTP_ERRORS,
    SSE_ACTIVE,
    SSE_STREAMS,
    JsonLogFormatter,
    bind_request_id,
    reset_request_id,
    start_internal_metrics_server,
    stop_internal_metrics_server,
)
from app.open_responses import iter_open_responses_sse


def _counter_value(metric, **labels: str) -> float:
    return float(metric.labels(**labels)._value.get())


def test_request_id_is_generated_or_preserved() -> None:
    with TestClient(app) as client:
        generated = client.get("/health")
        supplied = client.get("/health", headers={"X-Request-ID": "request-123"})
        invalid = client.get("/health", headers={"X-Request-ID": "valor con espacios"})

    assert re.fullmatch(r"[0-9a-f]{32}", generated.headers["x-request-id"])
    assert supplied.headers["x-request-id"] == "request-123"
    assert invalid.headers["x-request-id"] != "valor con espacios"


def test_metrics_endpoint_exports_application_metrics_in_development() -> None:
    metrics_app = create_app(
        Settings(_env_file=None, app_environment="development", metrics_enabled=True)
    )

    with TestClient(metrics_app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "agent_http_requests_total" in response.text
    assert "agent_openai_tokens_total" in response.text
    assert "agent_rag_search_duration_seconds" in response.text


def test_production_metrics_require_an_independent_key() -> None:
    metrics_key = "metrics-key-used-only-by-tests"
    metrics_app = create_app(
        Settings(
            _env_file=None,
            app_environment="production",
            metrics_enabled=True,
            metrics_api_key=SecretStr(metrics_key),
        )
    )

    with TestClient(metrics_app) as client:
        rejected = client.get("/metrics")
        accepted = client.get(
            "/metrics",
            headers={"Authorization": f"Bearer {metrics_key}"},
        )

    assert rejected.status_code == 401
    assert accepted.status_code == 200
    assert metrics_key not in accepted.text


def test_production_metrics_fail_closed_without_key() -> None:
    metrics_app = create_app(
        Settings(
            _env_file=None,
            app_environment="production",
            metrics_enabled=True,
            metrics_api_key=None,
        )
    )

    with TestClient(metrics_app) as client:
        response = client.get("/metrics")

    assert response.status_code == 503


def test_internal_metrics_server_is_bound_only_to_loopback() -> None:
    handle = start_internal_metrics_server(0)
    assert handle is not None
    server, _ = handle
    try:
        assert server.server_address[0] == "127.0.0.1"
        with urlopen(
            f"http://127.0.0.1:{server.server_port}/metrics",
            timeout=2,
        ) as response:
            body = response.read().decode("utf-8")
        assert "agent_http_requests_total" in body
    finally:
        stop_internal_metrics_server(handle)


def test_authentication_rejection_increments_401_metric(client: TestClient) -> None:
    before = _counter_value(
        HTTP_ERRORS,
        status_code="401",
        category="authentication",
    )

    response = client.post(
        "/v1/responses",
        json={"input": "Resume el perfil profesional."},
    )

    after = _counter_value(
        HTTP_ERRORS,
        status_code="401",
        category="authentication",
    )
    assert response.status_code == 401
    assert after == before + 1


def test_payload_rejection_increments_413_metric() -> None:
    limited_app = create_app(
        Settings(
            _env_file=None,
            max_request_body_bytes=1_024,
        )
    )
    before = _counter_value(
        HTTP_ERRORS,
        status_code="413",
        category="payload_too_large",
    )

    with TestClient(limited_app) as client:
        response = client.post(
            "/v1/responses",
            content=b"x" * 1_025,
            headers={"Content-Type": "application/json"},
        )

    after = _counter_value(
        HTTP_ERRORS,
        status_code="413",
        category="payload_too_large",
    )
    assert response.status_code == 413
    assert after == before + 1


class _RetrievalFailureAgent:
    def answer(self, request):
        raise RetrievalError("detalle interno")


def test_server_error_response_increments_5xx_metric(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    before = _counter_value(
        HTTP_ERRORS,
        status_code="503",
        category="server_error",
    )
    app.dependency_overrides[get_agent_service] = lambda: _RetrievalFailureAgent()
    try:
        response = client.post(
            "/v1/responses",
            json={"input": "Resume el perfil profesional."},
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.pop(get_agent_service, None)

    after = _counter_value(
        HTTP_ERRORS,
        status_code="503",
        category="server_error",
    )
    assert response.status_code == 503
    assert after == before + 1


def _stream_events():
    timestamp = int(time())
    result = GenerationResult(
        id="resp-observability-test",
        text="Respuesta simulada.",
        model="model-test",
        created_at=timestamp,
        completed_at=timestamp,
        status="completed",
        usage=GenerationUsage(input_tokens=2, output_tokens=2, total_tokens=4),
    )
    return iter(
        (
            GenerationStreamStarted(
                id=result.id,
                model=result.model,
                created_at=result.created_at,
            ),
            GenerationStreamCompleted(result=result),
        )
    )


def test_sse_completion_and_disconnection_are_measured() -> None:
    request = ResponseCreateRequest(input="Resume el perfil.", stream=True)
    settings = Settings(_env_file=None)
    completed_before = _counter_value(SSE_STREAMS, outcome="completed")
    disconnected_before = _counter_value(SSE_STREAMS, outcome="disconnected")
    active_before = float(SSE_ACTIVE._value.get())

    list(iter_open_responses_sse(request, _stream_events(), settings))
    interrupted = iter_open_responses_sse(request, _stream_events(), settings)
    next(interrupted)
    interrupted.close()

    assert _counter_value(SSE_STREAMS, outcome="completed") == completed_before + 1
    assert (
        _counter_value(SSE_STREAMS, outcome="disconnected") == disconnected_before + 1
    )
    assert float(SSE_ACTIVE._value.get()) == active_before


def test_json_logs_include_correlation_and_ignore_unapproved_fields() -> None:
    formatter = JsonLogFormatter(
        service="service-test",
        environment="test",
        version="1.0.0",
    )
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Evento seguro.",
        args=(),
        exc_info=None,
    )
    record.event = "test.event"
    record.authorization = "Bearer secreto"
    token = bind_request_id("correlation-test")
    try:
        payload = json.loads(formatter.format(record))
    finally:
        reset_request_id(token)

    assert payload["request_id"] == "correlation-test"
    assert payload["event"] == "test.event"
    assert "authorization" not in payload
    assert "secreto" not in json.dumps(payload)
