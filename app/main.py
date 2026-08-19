from time import time
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from app.auth import require_agent_access
from app.config import get_settings
from app.models import (
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

MOCK_RESPONSE_TEXT = (
    "Esta es una respuesta simulada del agente de CV. "
    "La integración con el modelo y el RAG se realizará en una actividad posterior."
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
    dependencies=[Depends(require_agent_access)],
)
def create_response(request: ResponseCreateRequest) -> ResponseResource:
    """Devuelve una respuesta Open Responses simulada para probar el contrato.

    Esta primera versión no consulta el RAG, no llama a un proveedor de IA y no
    consume créditos. Se sustituirá el texto fijo cuando se integre el flujo real.
    """

    if request.stream:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="El streaming SSE todavía no está implementado.",
        )

    timestamp = int(time())
    response_id = f"resp_{uuid4().hex}"
    message_id = f"msg_{uuid4().hex}"

    response_reasoning = None
    if request.reasoning is not None:
        response_reasoning = ResponseReasoning(
            effort=request.reasoning.effort,
            summary=request.reasoning.summary,
        )

    return ResponseResource(
        id=response_id,
        created_at=timestamp,
        completed_at=timestamp,
        status="completed",
        incomplete_details=None,
        model=request.model or "cv-agent-mock",
        previous_response_id=request.previous_response_id,
        instructions=request.instructions,
        output=[
            ResponseOutputMessage(
                id=message_id,
                status="completed",
                content=[
                    OutputTextContent(
                        type="output_text",
                        text=MOCK_RESPONSE_TEXT,
                    )
                ],
            )
        ],
        error=None,
        tools=request.tools or [],
        tool_choice=request.tool_choice or "auto",
        truncation=request.truncation,
        parallel_tool_calls=request.parallel_tool_calls or False,
        text=ResponseText(
            format=TextFormat(),
            verbosity=request.text.verbosity if request.text else None,
        ),
        top_p=request.top_p if request.top_p is not None else 1.0,
        presence_penalty=(
            request.presence_penalty if request.presence_penalty is not None else 0.0
        ),
        frequency_penalty=(
            request.frequency_penalty if request.frequency_penalty is not None else 0.0
        ),
        top_logprobs=request.top_logprobs or 0,
        temperature=request.temperature if request.temperature is not None else 1.0,
        reasoning=response_reasoning,
        usage=ResponseUsage(
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            input_tokens_details={"cached_tokens": 0},
            output_tokens_details={"reasoning_tokens": 0},
        ),
        max_output_tokens=request.max_output_tokens,
        max_tool_calls=request.max_tool_calls,
        store=request.store,
        background=request.background,
        service_tier=request.service_tier,
        metadata=dict(request.metadata or {}),
        safety_identifier=request.safety_identifier,
        prompt_cache_key=request.prompt_cache_key,
    )
