from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent import AgentService, RetrievalError
from app.config import get_settings
from app.dependencies import get_agent_service
from app.http_limits import RequestBodyLimitMiddleware
from app.llm import (
    GenerationConfigurationError,
    GenerationProviderError,
    GenerationRateLimitError,
    GenerationTimeoutError,
)
from app.models import ResponseCreateRequest, ResponseResource
from app.open_responses import build_completed_response, iter_open_responses_sse
from app.rate_limit import enforce_rate_limit


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    RequestBodyLimitMiddleware,
    max_bytes=settings.max_request_body_bytes,
)


@app.get("/health", response_model=HealthResponse, tags=["operación"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@app.post(
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
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        return StreamingResponse(
            iter_open_responses_sse(request, events, settings),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
            },
        )

    try:
        answer = agent_service.answer(request)
    except (GenerationConfigurationError, RetrievalError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except GenerationRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="El agente alcanzó temporalmente su límite de uso.",
        ) from exc
    except GenerationTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="El modelo excedió el tiempo máximo de respuesta.",
        ) from exc
    except GenerationProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El proveedor del modelo no pudo completar la respuesta.",
        ) from exc

    return build_completed_response(request, answer.generation, settings)
