import logging
from contextlib import asynccontextmanager
from hmac import compare_digest
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from app.agent import AgentService, RetrievalError
from app.config import Settings, get_settings
from app.dependencies import get_agent_service
from app.http_limits import RequestBodyLimitMiddleware
from app.llm import (
    GenerationConfigurationError,
    GenerationProviderError,
    GenerationRateLimitError,
    GenerationTimeoutError,
)
from app.models import ResponseCreateRequest, ResponseResource
from app.observability import (
    RequestObservabilityMiddleware,
    configure_logging,
    configure_sentry,
    instrument_fastapi,
    render_metrics,
    start_internal_metrics_server,
    stop_internal_metrics_server,
)
from app.open_responses import build_completed_response, iter_open_responses_sse
from app.rate_limit import enforce_rate_limit

logger = logging.getLogger(__name__)
PUBLIC_SERVICE_UNAVAILABLE = "El servicio no está disponible temporalmente."


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


def create_app(app_settings: Settings | None = None) -> FastAPI:
    """Construye la API con controles dependientes del entorno."""

    active_settings = app_settings or get_settings()
    is_production = active_settings.app_environment.casefold() == "production"
    configure_logging(active_settings)
    configure_sentry(active_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        metrics_server = (
            start_internal_metrics_server(active_settings.metrics_internal_port)
            if active_settings.metrics_enabled
            else None
        )
        try:
            yield
        finally:
            stop_internal_metrics_server(metrics_server)

    application = FastAPI(
        title=active_settings.app_name,
        version=active_settings.app_version,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
        lifespan=lifespan,
    )
    application.add_middleware(
        RequestBodyLimitMiddleware,
        max_bytes=active_settings.max_request_body_bytes,
    )

    @application.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    @application.get("/health", response_model=HealthResponse, tags=["operación"])
    def health() -> HealthResponse:
        return HealthResponse()

    if active_settings.metrics_enabled:

        @application.get("/metrics", include_in_schema=False)
        def metrics(request: Request) -> Response:
            """Expone métricas Prometheus sin publicar secretos operativos."""

            configured_key = active_settings.metrics_api_key
            if configured_key is not None:
                authorization = request.headers.get("authorization", "")
                scheme, _, supplied_key = authorization.partition(" ")
                if not (
                    scheme.casefold() == "bearer"
                    and supplied_key
                    and compare_digest(
                        supplied_key,
                        configured_key.get_secret_value(),
                    )
                ):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Credenciales inválidas.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            elif is_production:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Las métricas no están configuradas.",
                )

            body, content_type = render_metrics()
            return Response(
                content=body,
                headers={"Content-Type": content_type},
            )

    @application.post(
        "/v1/responses",
        response_model=ResponseResource,
        tags=["responses"],
        summary="Crear una respuesta del agente",
        dependencies=[Depends(enforce_rate_limit)],
    )
    def create_response(
        request: ResponseCreateRequest,
        agent_service: AgentService = Depends(get_agent_service),
    ) -> ResponseResource | StreamingResponse:
        """Recupera evidencia profesional y responde con JSON o SSE."""

        if request.stream:
            try:
                events = agent_service.stream(request)
            except RetrievalError as exc:
                logger.exception("Falló la recuperación previa al stream.")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=PUBLIC_SERVICE_UNAVAILABLE,
                ) from exc
            return StreamingResponse(
                iter_open_responses_sse(request, events, active_settings),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                },
            )

        try:
            answer = agent_service.answer(request)
        except (GenerationConfigurationError, RetrievalError) as exc:
            logger.exception("Falló la preparación de la respuesta del agente.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=PUBLIC_SERVICE_UNAVAILABLE,
            ) from exc
        except GenerationRateLimitError as exc:
            logger.warning(
                "El proveedor de generación rechazó la solicitud por límite.",
                extra={"event": "generation.rate_limit"},
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="El agente alcanzó temporalmente su límite de uso.",
            ) from exc
        except GenerationTimeoutError as exc:
            logger.error(
                "El proveedor de generación excedió el tiempo configurado.",
                extra={"event": "generation.timeout"},
            )
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="El modelo excedió el tiempo máximo de respuesta.",
            ) from exc
        except GenerationProviderError as exc:
            logger.exception(
                "El proveedor de generación no completó la respuesta.",
                extra={"event": "generation.provider_error"},
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="El proveedor del modelo no pudo completar la respuesta.",
            ) from exc

        return build_completed_response(
            request,
            answer.generation,
            active_settings,
        )

    application.add_middleware(
        RequestObservabilityMiddleware,
        excluded_paths={"/metrics"},
    )
    instrument_fastapi(application, active_settings)
    return application


settings = get_settings()
app = create_app(settings)
