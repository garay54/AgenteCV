from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from app.agent import AgentService, RetrievalError
from app.auth import require_agent_access
from app.config import get_settings
from app.dependencies import get_agent_service
from app.llm import (
    GenerationConfigurationError,
    GenerationProviderError,
    GenerationRateLimitError,
    GenerationTimeoutError,
)
from app.models import (
    IncompleteDetails,
    OutputTextContent,
    ResponseCreateRequest,
    ResponseOutputMessage,
    ResponseReasoning,
    ResponseResource,
    ResponseText,
    ResponseUsage,
    TextFormat,
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)


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
    dependencies=[Depends(require_agent_access)],
)
def create_response(
    request: ResponseCreateRequest,
    agent_service: AgentService = Depends(get_agent_service),
) -> ResponseResource:
    """Recupera evidencia profesional y genera una respuesta fundamentada."""

    if request.stream:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="El streaming SSE todavía no está implementado.",
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

    generation = answer.generation
    response_status = (
        generation.status
        if generation.status
        in {"completed", "failed", "in_progress", "cancelled", "queued", "incomplete"}
        else "completed"
    )
    effective_max_output_tokens = min(
        request.max_output_tokens or settings.generation_max_output_tokens,
        settings.generation_max_output_tokens,
    )

    return ResponseResource(
        id=generation.id,
        created_at=generation.created_at,
        completed_at=generation.completed_at,
        status=response_status,
        incomplete_details=(
            IncompleteDetails(reason=generation.incomplete_reason)
            if generation.incomplete_reason
            else None
        ),
        model=generation.model,
        previous_response_id=request.previous_response_id,
        instructions=request.instructions,
        output=[
            ResponseOutputMessage(
                id=f"msg_{uuid4().hex}",
                status="completed",
                content=[
                    OutputTextContent(
                        type="output_text",
                        text=generation.text,
                    )
                ],
            )
        ],
        error=None,
        tools=request.tools or [],
        tool_choice=request.tool_choice or "auto",
        truncation=request.truncation,
        parallel_tool_calls=False,
        text=ResponseText(
            format=TextFormat(),
            verbosity=settings.openai_text_verbosity,
        ),
        top_p=1.0,
        presence_penalty=0.0,
        frequency_penalty=0.0,
        top_logprobs=0,
        temperature=1.0,
        reasoning=ResponseReasoning(
            effort=settings.openai_reasoning_effort,
            summary=None,
        ),
        usage=ResponseUsage(
            input_tokens=generation.usage.input_tokens,
            output_tokens=generation.usage.output_tokens,
            total_tokens=generation.usage.total_tokens,
            input_tokens_details={
                "cached_tokens": generation.usage.cached_tokens
            },
            output_tokens_details={
                "reasoning_tokens": generation.usage.reasoning_tokens
            },
        ),
        max_output_tokens=effective_max_output_tokens,
        max_tool_calls=request.max_tool_calls,
        store=False,
        background=False,
        service_tier="default",
        metadata=dict(request.metadata or {}),
        safety_identifier=request.safety_identifier,
        prompt_cache_key=request.prompt_cache_key,
    )
