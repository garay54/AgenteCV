from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from time import time
from uuid import uuid4

from app.config import Settings
from app.llm import (
    GenerationProviderError,
    GenerationRateLimitError,
    GenerationResult,
    GenerationStreamCompleted,
    GenerationStreamEvent,
    GenerationStreamStarted,
    GenerationTextDelta,
    GenerationTimeoutError,
)
from app.models import (
    GenerationError,
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


def _effective_max_output_tokens(
    request: ResponseCreateRequest, settings: Settings
) -> int:
    return min(
        request.max_output_tokens or settings.generation_max_output_tokens,
        settings.generation_max_output_tokens,
    )


def _response_base(
    request: ResponseCreateRequest,
    settings: Settings,
) -> dict[str, object]:
    return {
        "previous_response_id": request.previous_response_id,
        "instructions": request.instructions,
        "tools": request.tools or [],
        "tool_choice": request.tool_choice or "auto",
        "truncation": request.truncation,
        "parallel_tool_calls": False,
        "text": ResponseText(
            format=TextFormat(),
            verbosity=settings.openai_text_verbosity,
        ),
        "top_p": 1.0,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "top_logprobs": 0,
        "temperature": 1.0,
        "reasoning": ResponseReasoning(
            effort=settings.openai_reasoning_effort,
            summary=None,
        ),
        "max_output_tokens": _effective_max_output_tokens(request, settings),
        "max_tool_calls": request.max_tool_calls,
        "store": False,
        "background": False,
        "service_tier": "default",
        "metadata": dict(request.metadata or {}),
        "safety_identifier": request.safety_identifier,
        "prompt_cache_key": request.prompt_cache_key,
    }


def build_completed_response(
    request: ResponseCreateRequest,
    generation: GenerationResult,
    settings: Settings,
    *,
    message_id: str | None = None,
) -> ResponseResource:
    response_status = (
        generation.status
        if generation.status
        in {"completed", "failed", "in_progress", "cancelled", "queued", "incomplete"}
        else "completed"
    )
    output_status = "incomplete" if response_status == "incomplete" else "completed"
    output_message = ResponseOutputMessage(
        id=message_id or f"msg_{uuid4().hex}",
        status=output_status,
        content=[OutputTextContent(type="output_text", text=generation.text)],
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
        output=[output_message],
        error=None,
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
        **_response_base(request, settings),
    )


def _build_progress_response(
    request: ResponseCreateRequest,
    started: GenerationStreamStarted,
    settings: Settings,
) -> ResponseResource:
    return ResponseResource(
        id=started.id,
        created_at=started.created_at,
        completed_at=None,
        status="in_progress",
        incomplete_details=None,
        model=started.model,
        output=[],
        error=None,
        usage=None,
        **_response_base(request, settings),
    )


def _build_failed_response(
    request: ResponseCreateRequest,
    started: GenerationStreamStarted,
    settings: Settings,
    *,
    message: str,
) -> ResponseResource:
    return ResponseResource(
        id=started.id,
        created_at=started.created_at,
        completed_at=int(time()),
        status="failed",
        incomplete_details=None,
        model=started.model,
        output=[],
        error=GenerationError(code="model_error", message=message),
        usage=None,
        **_response_base(request, settings),
    )


def _sse_event(event_type: str, payload: dict[str, object]) -> str:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event_type}\ndata: {data}\n\n"


def _public_error(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, GenerationRateLimitError):
        return "rate_limit_exceeded", "El agente alcanzó temporalmente su límite de uso."
    if isinstance(exc, GenerationTimeoutError):
        return "model_timeout", "El modelo excedió el tiempo máximo de respuesta."
    return "model_error", "El proveedor no pudo completar la respuesta."


def iter_open_responses_sse(
    request: ResponseCreateRequest,
    events: Iterable[GenerationStreamEvent],
    settings: Settings,
) -> Iterator[str]:
    """Transforma deltas internos al ciclo SSE normativo de Open Responses."""

    sequence_number = 0
    started: GenerationStreamStarted | None = None
    message_id = f"msg_{uuid4().hex}"
    accumulated_text: list[str] = []
    completed = False

    try:
        for event in events:
            if isinstance(event, GenerationStreamStarted):
                started = event
                response = _build_progress_response(request, started, settings)
                response_data = response.model_dump(mode="json")

                yield _sse_event(
                    "response.created",
                    {
                        "type": "response.created",
                        "sequence_number": sequence_number,
                        "response": response_data,
                    },
                )
                sequence_number += 1
                yield _sse_event(
                    "response.in_progress",
                    {
                        "type": "response.in_progress",
                        "sequence_number": sequence_number,
                        "response": response_data,
                    },
                )
                sequence_number += 1

                item = {
                    "id": message_id,
                    "type": "message",
                    "status": "in_progress",
                    "role": "assistant",
                    "content": [],
                }
                yield _sse_event(
                    "response.output_item.added",
                    {
                        "type": "response.output_item.added",
                        "sequence_number": sequence_number,
                        "output_index": 0,
                        "item": item,
                    },
                )
                sequence_number += 1

                empty_part = {
                    "type": "output_text",
                    "annotations": [],
                    "text": "",
                }
                yield _sse_event(
                    "response.content_part.added",
                    {
                        "type": "response.content_part.added",
                        "sequence_number": sequence_number,
                        "item_id": message_id,
                        "output_index": 0,
                        "content_index": 0,
                        "part": empty_part,
                    },
                )
                sequence_number += 1

            elif isinstance(event, GenerationTextDelta):
                if started is None:
                    raise GenerationProviderError(
                        "El proveedor envió texto antes de iniciar la respuesta."
                    )
                accumulated_text.append(event.delta)
                yield _sse_event(
                    "response.output_text.delta",
                    {
                        "type": "response.output_text.delta",
                        "sequence_number": sequence_number,
                        "item_id": message_id,
                        "output_index": 0,
                        "content_index": 0,
                        "delta": event.delta,
                        "logprobs": [],
                    },
                )
                sequence_number += 1

            elif isinstance(event, GenerationStreamCompleted):
                if started is None:
                    started = GenerationStreamStarted(
                        id=event.result.id,
                        model=event.result.model,
                        created_at=event.result.created_at,
                    )
                final_text = event.result.text or "".join(accumulated_text)
                final_part = OutputTextContent(type="output_text", text=final_text)
                final_item = ResponseOutputMessage(
                    id=message_id,
                    status=(
                        "incomplete"
                        if event.result.status == "incomplete"
                        else "completed"
                    ),
                    content=[final_part],
                )

                yield _sse_event(
                    "response.output_text.done",
                    {
                        "type": "response.output_text.done",
                        "sequence_number": sequence_number,
                        "item_id": message_id,
                        "output_index": 0,
                        "content_index": 0,
                        "text": final_text,
                        "logprobs": [],
                    },
                )
                sequence_number += 1
                yield _sse_event(
                    "response.content_part.done",
                    {
                        "type": "response.content_part.done",
                        "sequence_number": sequence_number,
                        "item_id": message_id,
                        "output_index": 0,
                        "content_index": 0,
                        "part": final_part.model_dump(mode="json"),
                    },
                )
                sequence_number += 1
                yield _sse_event(
                    "response.output_item.done",
                    {
                        "type": "response.output_item.done",
                        "sequence_number": sequence_number,
                        "output_index": 0,
                        "item": final_item.model_dump(mode="json"),
                    },
                )
                sequence_number += 1

                response = build_completed_response(
                    request,
                    event.result,
                    settings,
                    message_id=message_id,
                )
                terminal_type = (
                    "response.incomplete"
                    if event.result.status == "incomplete"
                    else "response.completed"
                )
                yield _sse_event(
                    terminal_type,
                    {
                        "type": terminal_type,
                        "sequence_number": sequence_number,
                        "response": response.model_dump(mode="json"),
                    },
                )
                sequence_number += 1
                yield "data: [DONE]\n\n"
                completed = True
                return

        if not completed:
            raise GenerationProviderError(
                "El proveedor cerró el stream sin un evento terminal."
            )
    except Exception as exc:
        if started is None:
            started = GenerationStreamStarted(
                id=f"resp_{uuid4().hex}",
                model=settings.openai_generation_model,
                created_at=int(time()),
            )
        code, message = _public_error(exc)
        yield _sse_event(
            "error",
            {
                "type": "error",
                "sequence_number": sequence_number,
                "error": {
                    "message": message,
                    "type": "model_error",
                    "param": None,
                    "code": code,
                },
            },
        )
        sequence_number += 1
        failed_response = _build_failed_response(
            request,
            started,
            settings,
            message=message,
        )
        yield _sse_event(
            "response.failed",
            {
                "type": "response.failed",
                "sequence_number": sequence_number,
                "response": failed_response.model_dump(mode="json"),
            },
        )
        yield "data: [DONE]\n\n"
