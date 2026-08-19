import json
from time import time

import pytest
from fastapi.testclient import TestClient

from app.agent import AgentAnswer
from app.dependencies import get_agent_service
from app.llm import (
    GenerationRateLimitError,
    GenerationResult,
    GenerationStreamCompleted,
    GenerationStreamStarted,
    GenerationTextDelta,
    GenerationTimeoutError,
    GenerationUsage,
)
from app.main import app
from app.models import ResponseResource


STUB_RESPONSE_TEXT = (
    "Mario cuenta con experiencia documentada en investigación y desarrollo de "
    "sistemas de inteligencia artificial."
)


class _AgentStub:
    def answer(self, request) -> AgentAnswer:
        timestamp = int(time())
        return AgentAnswer(
            generation=GenerationResult(
                id="resp_stub_001",
                text=STUB_RESPONSE_TEXT,
                model="gpt-5.6-luna",
                created_at=timestamp,
                completed_at=timestamp,
                status="completed",
                usage=GenerationUsage(
                    input_tokens=120,
                    output_tokens=24,
                    total_tokens=144,
                ),
            ),
            retrieved=(),
        )

    def stream(self, request):
        timestamp = int(time())
        result = GenerationResult(
            id="resp_stream_stub_001",
            text=STUB_RESPONSE_TEXT,
            model="gpt-5.6-luna",
            created_at=timestamp,
            completed_at=timestamp,
            status="completed",
            usage=GenerationUsage(
                input_tokens=120,
                output_tokens=24,
                total_tokens=144,
            ),
        )
        return iter(
            (
                GenerationStreamStarted(
                    id=result.id,
                    model=result.model,
                    created_at=result.created_at,
                ),
                GenerationTextDelta(delta="Mario cuenta con experiencia "),
                GenerationTextDelta(
                    delta="documentada en inteligencia artificial."
                ),
                GenerationStreamCompleted(result=result),
            )
        )


class _RateLimitedAgentStub:
    def answer(self, request) -> AgentAnswer:
        raise GenerationRateLimitError("detalle interno no publicable")


class _StreamingTimeoutAgentStub:
    def stream(self, request):
        yield GenerationStreamStarted(
            id="resp_stream_timeout_001",
            model="gpt-5.6-luna",
            created_at=int(time()),
        )
        raise GenerationTimeoutError("detalle interno no publicable")


@pytest.fixture
def generated_client(client: TestClient):
    app.dependency_overrides[get_agent_service] = lambda: _AgentStub()
    yield client
    app.dependency_overrides.pop(get_agent_service, None)


def test_non_streaming_response_satisfies_contract_without_network_call(
    generated_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = generated_client.post(
        "/v1/responses",
        json={
            "model": "modelo-no-autorizado-del-cliente",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "¿Cuál es la experiencia profesional de Mario?",
                        }
                    ],
                }
            ],
            "stream": False,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    contract = ResponseResource.model_validate(response.json())
    assert contract.object == "response"
    assert contract.status == "completed"
    assert contract.model == "gpt-5.6-luna"
    assert contract.id == "resp_stub_001"
    assert contract.output[0].id.startswith("msg_")
    assert contract.output[0].role == "assistant"
    assert contract.output[0].content[0].text == STUB_RESPONSE_TEXT
    assert contract.usage is not None
    assert contract.usage.total_tokens == 144
    assert contract.reasoning is not None
    assert contract.reasoning.effort == "none"


def test_minimal_string_request_uses_configured_generation_model(
    generated_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = generated_client.post(
        "/v1/responses",
        json={"input": "Resume el perfil profesional de Mario."},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["model"] == "gpt-5.6-luna"


def test_streaming_emits_open_responses_event_lifecycle(
    generated_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = generated_client.post(
        "/v1/responses",
        json={"input": "Resume el perfil profesional de Mario.", "stream": True},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    lines = [line for line in response.text.splitlines() if line]
    event_names = [
        line.removeprefix("event: ")
        for line in lines
        if line.startswith("event: ")
    ]
    assert event_names == [
        "response.created",
        "response.in_progress",
        "response.output_item.added",
        "response.content_part.added",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.done",
        "response.content_part.done",
        "response.output_item.done",
        "response.completed",
    ]
    assert lines[-1] == "data: [DONE]"

    payloads = [
        json.loads(line.removeprefix("data: "))
        for line in lines
        if line.startswith("data: {")
    ]
    assert [payload["sequence_number"] for payload in payloads] == list(
        range(len(payloads))
    )
    completed = payloads[-1]["response"]
    assert completed["model"] == "gpt-5.6-luna"
    assert completed["status"] == "completed"
    assert completed["usage"]["total_tokens"] == 144
    assert "fuentes_profesionales" not in response.text
    assert "SRC-" not in response.text


def test_streaming_error_is_sanitized_and_closed(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    app.dependency_overrides[get_agent_service] = lambda: _StreamingTimeoutAgentStub()
    try:
        response = client.post(
            "/v1/responses",
            json={"input": "Resume el perfil de Mario.", "stream": True},
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.pop(get_agent_service, None)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: error" in response.text
    assert "event: response.failed" in response.text
    assert response.text.rstrip().endswith("data: [DONE]")
    assert "model_timeout" in response.text
    assert "detalle interno" not in response.text


def test_provider_rate_limit_is_mapped_without_leaking_details(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    app.dependency_overrides[get_agent_service] = lambda: _RateLimitedAgentStub()
    try:
        response = client.post(
            "/v1/responses",
            json={"input": "Resume el perfil profesional de Mario."},
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.pop(get_agent_service, None)

    assert response.status_code == 429
    assert response.json() == {
        "detail": "El agente alcanzó temporalmente su límite de uso."
    }
    assert "detalle interno" not in response.text
