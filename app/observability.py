"""Observabilidad segura para HTTP, RAG, proveedores y streaming.

Este módulo evita deliberadamente registrar cuerpos HTTP, credenciales,
consultas, respuestas del modelo o fragmentos recuperados.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from time import perf_counter
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse
from uuid import uuid4

from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    start_http_server,
)
from starlette.types import ASGIApp, Message, Receive, Scope, Send

if TYPE_CHECKING:
    from app.config import Settings
    from app.llm import GenerationUsage


LOGGER = logging.getLogger(__name__)
_REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_LOGGING_CONFIGURED = False
_SENTRY_CONFIGURED = False
_TRACER_PROVIDER: Any | None = None
_INTERNAL_METRICS_SERVER: tuple[Any, Any] | None = None

_LOG_FIELDS = {
    "client_disconnected",
    "duration_ms",
    "error_category",
    "error_type",
    "event",
    "input_tokens",
    "method",
    "model",
    "operation",
    "outcome",
    "output_tokens",
    "provider_request_id",
    "result_count",
    "route",
    "status_code",
    "stream",
    "token_type",
    "top_score",
    "total_tokens",
}


HTTP_REQUESTS = Counter(
    "agent_http_requests_total",
    "Solicitudes HTTP finalizadas.",
    ("method", "route", "status_code"),
)
HTTP_REQUEST_DURATION = Histogram(
    "agent_http_request_duration_seconds",
    "Duración completa de solicitudes HTTP, incluidos streams.",
    ("method", "route"),
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)
HTTP_ERRORS = Counter(
    "agent_http_errors_total",
    "Errores HTTP relevantes para operación y seguridad.",
    ("status_code", "category"),
)
SSE_ACTIVE = Gauge(
    "agent_sse_active_streams",
    "Streams SSE actualmente abiertos.",
)
SSE_STREAMS = Counter(
    "agent_sse_streams_total",
    "Streams SSE terminados por resultado.",
    ("outcome",),
)
SSE_DURATION = Histogram(
    "agent_sse_stream_duration_seconds",
    "Duración de streams SSE.",
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)
OPENAI_REQUESTS = Counter(
    "agent_openai_requests_total",
    "Solicitudes al proveedor de IA por operación y resultado.",
    ("operation", "model", "outcome"),
)
OPENAI_DURATION = Histogram(
    "agent_openai_request_duration_seconds",
    "Duración de solicitudes al proveedor de IA.",
    ("operation", "model"),
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)
OPENAI_TOKENS = Counter(
    "agent_openai_tokens_total",
    "Tokens informados por el proveedor de IA.",
    ("operation", "model", "token_type"),
)
RAG_SEARCHES = Counter(
    "agent_rag_searches_total",
    "Búsquedas RAG por resultado.",
    ("outcome",),
)
RAG_DURATION = Histogram(
    "agent_rag_search_duration_seconds",
    "Duración completa de búsquedas RAG.",
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
RAG_RESULT_COUNT = Histogram(
    "agent_rag_result_count",
    "Cantidad de fragmentos seleccionados por búsqueda.",
    buckets=(0, 1, 2, 3, 4, 6, 8, 12, 16),
)
RAG_TOP_SCORE = Histogram(
    "agent_rag_top_score",
    "Mejor similitud coseno seleccionada por búsqueda.",
    buckets=(0, 0.25, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1),
)


def current_request_id() -> str | None:
    """Devuelve el identificador de la solicitud en el contexto actual."""

    return _REQUEST_ID.get()


def bind_request_id(value: str) -> Token[str | None]:
    return _REQUEST_ID.set(value)


def reset_request_id(token: Token[str | None]) -> None:
    _REQUEST_ID.reset(token)


def _trace_context() -> tuple[str | None, str | None]:
    context = trace.get_current_span().get_span_context()
    if not context.is_valid:
        return None, None
    return f"{context.trace_id:032x}", f"{context.span_id:016x}"


class JsonLogFormatter(logging.Formatter):
    """Serializa registros en una sola línea apta para agregadores cloud."""

    def __init__(self, *, service: str, environment: str, version: str) -> None:
        super().__init__()
        self.service = service
        self.environment = environment
        self.version = version

    def format(self, record: logging.LogRecord) -> str:
        trace_id, span_id = _trace_context()
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "severity": record.levelname,
            "service": self.service,
            "environment": self.environment,
            "version": self.version,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = current_request_id()
        if request_id:
            payload["request_id"] = request_id
        if trace_id:
            payload["trace_id"] = trace_id
            payload["span_id"] = span_id
        for field in _LOG_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = {
                "type": record.exc_info[0].__name__,
                "stacktrace": self.formatException(record.exc_info),
            }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(settings: Settings) -> None:
    """Configura una salida JSON única sin alterar el contenido de los eventos."""

    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_json:
        handler.setFormatter(
            JsonLogFormatter(
                service=settings.otel_service_name,
                environment=settings.app_environment,
                version=settings.app_version,
            )
        )
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(settings.log_level.upper())
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
    for logger_name in ("httpcore", "httpx", "openai"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    _LOGGING_CONFIGURED = True


def _scrub_sentry_event(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any]:
    del hint
    request = event.get("request")
    if isinstance(request, dict):
        request.pop("data", None)
        request.pop("cookies", None)
        headers = request.get("headers")
        if isinstance(headers, dict):
            for name in tuple(headers):
                if name.casefold() in {
                    "authorization",
                    "cookie",
                    "proxy-authorization",
                    "x-api-key",
                }:
                    headers[name] = "[Filtered]"
    return event


def configure_sentry(settings: Settings) -> None:
    """Activa Sentry sólo cuando existe un DSN explícito."""

    global _SENTRY_CONFIGURED
    if _SENTRY_CONFIGURED or settings.sentry_dsn is None:
        return

    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn.get_secret_value(),
        environment=settings.app_environment,
        release=settings.app_version,
        send_default_pii=False,
        max_request_body_size="never",
        include_local_variables=False,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        before_send=_scrub_sentry_event,
    )
    _SENTRY_CONFIGURED = True


def _otlp_headers(raw: str | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in (raw or "").split(","):
        name, separator, value = item.partition("=")
        if separator and name.strip() and value.strip():
            headers[name.strip()] = value.strip()
    return headers


def configure_open_telemetry(settings: Settings) -> Any | None:
    """Configura exportación OTLP/HTTP y propagación W3C para el proceso."""

    global _TRACER_PROVIDER
    if not settings.otel_enabled:
        return None
    if _TRACER_PROVIDER is not None:
        return _TRACER_PROVIDER
    if not settings.otel_exporter_otlp_traces_endpoint:
        LOGGER.warning(
            "OpenTelemetry está habilitado sin un endpoint OTLP.",
            extra={"event": "otel.configuration.invalid"},
        )
        return None

    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

    resource_attributes = {
        "service.name": settings.otel_service_name,
        "service.version": settings.app_version,
        "deployment.environment.name": settings.app_environment,
    }
    raw_headers = (
        settings.otel_exporter_otlp_headers.get_secret_value()
        if settings.otel_exporter_otlp_headers is not None
        else None
    )
    exporter_arguments: dict[str, Any] = {
        "endpoint": settings.otel_exporter_otlp_traces_endpoint,
        "headers": _otlp_headers(raw_headers),
        "timeout": settings.otel_export_timeout_seconds,
    }
    endpoint_host = urlparse(settings.otel_exporter_otlp_traces_endpoint).hostname
    if endpoint_host == "telemetry.googleapis.com":
        import google.auth
        from google.auth.transport.requests import AuthorizedSession

        credentials, detected_project_id = google.auth.default(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )
        exporter_arguments["session"] = AuthorizedSession(credentials)
        if detected_project_id:
            resource_attributes["gcp.project_id"] = detected_project_id

    provider = TracerProvider(
        resource=Resource.create(resource_attributes),
        sampler=ParentBased(TraceIdRatioBased(settings.otel_trace_sample_ratio)),
    )
    exporter = OTLPSpanExporter(**exporter_arguments)
    provider.add_span_processor(
        BatchSpanProcessor(
            exporter,
            schedule_delay_millis=1_000,
            export_timeout_millis=int(settings.otel_export_timeout_seconds * 1_000),
        )
    )
    trace.set_tracer_provider(provider)
    HTTPXClientInstrumentor().instrument(tracer_provider=provider)
    _TRACER_PROVIDER = provider
    return provider


def instrument_fastapi(application: Any, settings: Settings) -> None:
    """Añade spans de servidor HTTP a una aplicación FastAPI."""

    provider = configure_open_telemetry(settings)
    if provider is None:
        return
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(
        application,
        tracer_provider=provider,
        excluded_urls="/health,/metrics",
    )


def tracer() -> Any:
    return trace.get_tracer("agent.application")


def set_span_attributes(span: Span, **attributes: object) -> None:
    if not span.is_recording():
        return
    for name, value in attributes.items():
        if value is not None:
            span.set_attribute(name, value)  # type: ignore[arg-type]


def mark_span_error(span: Span, exc: BaseException) -> None:
    if not span.is_recording():
        return
    span.record_exception(exc)
    span.set_status(Status(StatusCode.ERROR, type(exc).__name__))


def openai_request_headers() -> dict[str, str]:
    """Propaga la correlación propia sin revelar el identificador al modelo."""

    request_id = current_request_id()
    return {"X-Client-Request-Id": request_id} if request_id else {}


def _provider_request_id(response: Any) -> str | None:
    value = getattr(response, "_request_id", None)
    return str(value) if value else None


def record_openai_request(
    *,
    operation: str,
    model: str,
    outcome: str,
    duration_seconds: float,
    usage: GenerationUsage | None = None,
    response: Any | None = None,
    error: BaseException | None = None,
) -> None:
    OPENAI_REQUESTS.labels(operation=operation, model=model, outcome=outcome).inc()
    OPENAI_DURATION.labels(operation=operation, model=model).observe(duration_seconds)
    token_values = {
        "input": usage.input_tokens if usage else 0,
        "output": usage.output_tokens if usage else 0,
        "total": usage.total_tokens if usage else 0,
        "cached": usage.cached_tokens if usage else 0,
        "reasoning": usage.reasoning_tokens if usage else 0,
    }
    for token_type, value in token_values.items():
        if value:
            OPENAI_TOKENS.labels(
                operation=operation,
                model=model,
                token_type=token_type,
            ).inc(value)

    provider_request_id = _provider_request_id(response)
    level = logging.INFO if outcome == "success" else logging.ERROR
    LOGGER.log(
        level,
        "Solicitud al proveedor de IA finalizada.",
        extra={
            "event": "openai.request.finished",
            "operation": operation,
            "model": model,
            "outcome": outcome,
            "duration_ms": round(duration_seconds * 1000, 3),
            "input_tokens": token_values["input"],
            "output_tokens": token_values["output"],
            "total_tokens": token_values["total"],
            "provider_request_id": provider_request_id,
            "error_type": type(error).__name__ if error else None,
        },
    )


def record_rag_search(
    *,
    outcome: str,
    duration_seconds: float,
    result_count: int = 0,
    top_score: float | None = None,
    error: BaseException | None = None,
) -> None:
    RAG_SEARCHES.labels(outcome=outcome).inc()
    RAG_DURATION.observe(duration_seconds)
    if outcome == "success":
        RAG_RESULT_COUNT.observe(result_count)
        RAG_TOP_SCORE.observe(top_score if top_score is not None else 0.0)
    LOGGER.log(
        logging.INFO if outcome == "success" else logging.ERROR,
        "Búsqueda RAG finalizada.",
        extra={
            "event": "rag.search.finished",
            "outcome": outcome,
            "duration_ms": round(duration_seconds * 1000, 3),
            "result_count": result_count,
            "top_score": round(top_score, 6) if top_score is not None else None,
            "error_type": type(error).__name__ if error else None,
        },
    )


def sse_stream_started() -> float:
    SSE_ACTIVE.inc()
    return perf_counter()


def record_sse_stream(
    *, outcome: str, started_at: float, error: BaseException | None = None
) -> None:
    duration = perf_counter() - started_at
    SSE_ACTIVE.dec()
    SSE_STREAMS.labels(outcome=outcome).inc()
    SSE_DURATION.observe(duration)
    level = logging.INFO if outcome == "completed" else logging.WARNING
    LOGGER.log(
        level,
        "Stream SSE finalizado.",
        extra={
            "event": "sse.stream.finished",
            "outcome": outcome,
            "duration_ms": round(duration * 1000, 3),
            "error_type": type(error).__name__ if error else None,
        },
    )


def log_security_event(event: str, *, status_code: int) -> None:
    LOGGER.warning(
        "Control de acceso HTTP rechazó la solicitud.",
        extra={"event": event, "status_code": status_code},
    )


def _error_category(status_code: int) -> str | None:
    if status_code == 401:
        return "authentication"
    if status_code == 413:
        return "payload_too_large"
    if status_code == 429:
        return "rate_limit"
    if status_code >= 500:
        return "server_error"
    return None


def _route_label(scope: Scope) -> str:
    route = scope.get("route")
    route_path = getattr(route, "path", None)
    if route_path:
        return str(route_path)
    path = str(scope.get("path", ""))
    if path in {
        "/health",
        "/metrics",
        "/v1/responses",
        "/docs",
        "/redoc",
        "/openapi.json",
    }:
        return path
    return "unmatched"


def record_http_request(
    *,
    method: str,
    route: str,
    status_code: int,
    duration_seconds: float,
    client_disconnected: bool,
    error: BaseException | None = None,
) -> None:
    HTTP_REQUESTS.labels(
        method=method,
        route=route,
        status_code=str(status_code),
    ).inc()
    HTTP_REQUEST_DURATION.labels(method=method, route=route).observe(duration_seconds)
    category = _error_category(status_code)
    if category:
        HTTP_ERRORS.labels(status_code=str(status_code), category=category).inc()
    LOGGER.log(
        logging.ERROR if status_code >= 500 else logging.INFO,
        "Solicitud HTTP finalizada.",
        extra={
            "event": "http.request.finished",
            "method": method,
            "route": route,
            "status_code": status_code,
            "duration_ms": round(duration_seconds * 1000, 3),
            "client_disconnected": client_disconnected,
            "error_category": category,
            "error_type": type(error).__name__ if error else None,
        },
    )


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


def start_internal_metrics_server(port: int | None) -> tuple[Any, Any] | None:
    """Expone Prometheus sólo en loopback para un sidecar del mismo servicio."""

    global _INTERNAL_METRICS_SERVER
    if port is None:
        return None
    if _INTERNAL_METRICS_SERVER is not None:
        return _INTERNAL_METRICS_SERVER

    server, thread = start_http_server(port, addr="127.0.0.1")
    _INTERNAL_METRICS_SERVER = (server, thread)
    LOGGER.info(
        "Servidor interno de métricas iniciado.",
        extra={"event": "metrics.internal.started"},
    )
    return _INTERNAL_METRICS_SERVER


def stop_internal_metrics_server(handle: tuple[Any, Any] | None) -> None:
    """Cierra limpiamente el servidor interno sin afectar `/metrics`."""

    global _INTERNAL_METRICS_SERVER
    if handle is None:
        return
    server, thread = handle
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    if _INTERNAL_METRICS_SERVER == handle:
        _INTERNAL_METRICS_SERVER = None
    LOGGER.info(
        "Servidor interno de métricas detenido.",
        extra={"event": "metrics.internal.stopped"},
    )


class RequestObservabilityMiddleware:
    """Correlaciona y mide el ciclo ASGI completo, incluido el cuerpo SSE."""

    def __init__(self, app: ASGIApp, *, excluded_paths: set[str] | None = None) -> None:
        self.app = app
        self.excluded_paths = excluded_paths or set()

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        supplied_id = headers.get(b"x-request-id", b"").decode("ascii", errors="ignore")
        request_id = (
            supplied_id if _REQUEST_ID_RE.fullmatch(supplied_id) else uuid4().hex
        )
        token = bind_request_id(request_id)
        started_at = perf_counter()
        status_code = 500
        response_started = False
        client_disconnected = False
        failure: BaseException | None = None

        async def observed_receive() -> Message:
            nonlocal client_disconnected
            message = await receive()
            if message["type"] == "http.disconnect":
                client_disconnected = True
            return message

        async def observed_send(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])
                response_headers = list(message.get("headers", []))
                response_headers = [
                    (name, value)
                    for name, value in response_headers
                    if name.lower() != b"x-request-id"
                ]
                response_headers.append((b"x-request-id", request_id.encode("ascii")))
                message["headers"] = response_headers
            await send(message)

        try:
            await self.app(scope, observed_receive, observed_send)
        except BaseException as exc:
            failure = exc
            if not response_started:
                status_code = 500
            raise
        finally:
            try:
                if str(scope.get("path", "")) not in self.excluded_paths:
                    record_http_request(
                        method=str(scope.get("method", "UNKNOWN")),
                        route=_route_label(scope),
                        status_code=status_code,
                        duration_seconds=perf_counter() - started_at,
                        client_disconnected=client_disconnected,
                        error=failure,
                    )
            finally:
                reset_request_id(token)
