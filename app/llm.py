from __future__ import annotations

from collections.abc import Iterator
from contextlib import suppress
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Literal, Protocol

from opentelemetry import trace as otel_trace

from app.observability import (
    mark_span_error,
    openai_request_headers,
    record_openai_request,
    set_span_attributes,
    tracer,
)

ProviderInput = str | list[dict[str, str]]
ReasoningEffort = Literal["none", "low", "medium", "high", "xhigh", "max"]
TextVerbosity = Literal["low", "medium", "high"]


class GenerationConfigurationError(RuntimeError):
    """Falta configuración necesaria para invocar el modelo."""


class GenerationProviderError(RuntimeError):
    """El proveedor no pudo producir una respuesta utilizable."""


class GenerationTimeoutError(GenerationProviderError):
    """La llamada al proveedor excedió el tiempo configurado."""


class GenerationRateLimitError(GenerationProviderError):
    """El proveedor rechazó temporalmente la llamada por cuota o frecuencia."""


@dataclass(frozen=True, slots=True)
class GenerationUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0


@dataclass(frozen=True, slots=True)
class GenerationResult:
    id: str
    text: str
    model: str
    created_at: int
    completed_at: int | None
    status: str
    usage: GenerationUsage
    incomplete_reason: str | None = None


@dataclass(frozen=True, slots=True)
class GenerationStreamStarted:
    id: str
    model: str
    created_at: int


@dataclass(frozen=True, slots=True)
class GenerationTextDelta:
    delta: str


@dataclass(frozen=True, slots=True)
class GenerationStreamCompleted:
    result: GenerationResult


GenerationStreamEvent = (
    GenerationStreamStarted | GenerationTextDelta | GenerationStreamCompleted
)


class GenerationProvider(Protocol):
    @property
    def model_name(self) -> str: ...

    def generate(
        self,
        *,
        input_data: ProviderInput,
        instructions: str,
        max_output_tokens: int,
    ) -> GenerationResult: ...

    def stream(
        self,
        *,
        input_data: ProviderInput,
        instructions: str,
        max_output_tokens: int,
    ) -> Iterator[GenerationStreamEvent]: ...


def _integer_attribute(value: Any, name: str) -> int:
    raw = getattr(value, name, 0) if value is not None else 0
    return int(raw or 0)


def _result_from_response(response: Any, *, text: str) -> GenerationResult:
    usage = getattr(response, "usage", None)
    input_details = getattr(usage, "input_tokens_details", None)
    output_details = getattr(usage, "output_tokens_details", None)
    incomplete_details = getattr(response, "incomplete_details", None)

    return GenerationResult(
        id=str(response.id),
        text=text.strip(),
        model=str(getattr(response, "model", "") or ""),
        created_at=int(response.created_at),
        completed_at=(
            int(response.completed_at)
            if getattr(response, "completed_at", None) is not None
            else None
        ),
        status=str(getattr(response, "status", "completed") or "completed"),
        incomplete_reason=(
            str(incomplete_details.reason)
            if incomplete_details is not None
            and getattr(incomplete_details, "reason", None)
            else None
        ),
        usage=GenerationUsage(
            input_tokens=_integer_attribute(usage, "input_tokens"),
            output_tokens=_integer_attribute(usage, "output_tokens"),
            total_tokens=_integer_attribute(usage, "total_tokens"),
            cached_tokens=_integer_attribute(input_details, "cached_tokens"),
            reasoning_tokens=_integer_attribute(output_details, "reasoning_tokens"),
        ),
    )


class OpenAIResponsesProvider:
    """Adaptador del SDK de OpenAI hacia el contrato interno del agente."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str = "gpt-5.6-luna",
        reasoning_effort: ReasoningEffort = "none",
        text_verbosity: TextVerbosity = "low",
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
        client: Any | None = None,
    ) -> None:
        if not api_key and client is None:
            raise GenerationConfigurationError(
                "Falta OPENAI_API_KEY para generar respuestas."
            )

        if client is None:
            from openai import OpenAI

            client = OpenAI(
                api_key=api_key,
                timeout=timeout_seconds,
                max_retries=max_retries,
            )

        self._client = client
        self._model = model
        self._reasoning_effort = reasoning_effort
        self._text_verbosity = text_verbosity

    @property
    def model_name(self) -> str:
        return self._model

    def generate(
        self,
        *,
        input_data: ProviderInput,
        instructions: str,
        max_output_tokens: int,
    ) -> GenerationResult:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            RateLimitError,
        )

        operation = "responses.create"
        started_at = perf_counter()
        headers = openai_request_headers()
        request_options = {"extra_headers": headers} if headers else {}
        with tracer().start_as_current_span("openai.responses.create") as span:
            set_span_attributes(
                span,
                **{
                    "gen_ai.system": "openai",
                    "gen_ai.operation.name": "responses",
                    "gen_ai.request.model": self._model,
                    "gen_ai.request.max_tokens": max_output_tokens,
                },
            )
            try:
                response = self._client.responses.create(
                    model=self._model,
                    input=input_data,
                    instructions=instructions,
                    max_output_tokens=max_output_tokens,
                    reasoning={"effort": self._reasoning_effort},
                    text={"verbosity": self._text_verbosity},
                    store=False,
                    stream=False,
                    **request_options,
                )
            except APITimeoutError as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="timeout",
                    duration_seconds=perf_counter() - started_at,
                    error=exc,
                )
                raise GenerationTimeoutError(
                    "El proveedor excedió el tiempo de respuesta."
                ) from exc
            except RateLimitError as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="rate_limit",
                    duration_seconds=perf_counter() - started_at,
                    error=exc,
                )
                raise GenerationRateLimitError(
                    "El proveedor no tiene cuota disponible temporalmente."
                ) from exc
            except (APIConnectionError, APIStatusError) as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="provider_error",
                    duration_seconds=perf_counter() - started_at,
                    error=exc,
                )
                raise GenerationProviderError(
                    "El proveedor de generación no está disponible."
                ) from exc

            try:
                text = str(getattr(response, "output_text", "") or "").strip()
                if not text:
                    raise GenerationProviderError(
                        "El proveedor terminó la solicitud sin texto utilizable."
                    )
                result = _result_from_response(response, text=text)
                if not result.model:
                    result = GenerationResult(
                        id=result.id,
                        text=result.text,
                        model=self._model,
                        created_at=result.created_at,
                        completed_at=result.completed_at,
                        status=result.status,
                        usage=result.usage,
                        incomplete_reason=result.incomplete_reason,
                    )
            except Exception as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="invalid_response",
                    duration_seconds=perf_counter() - started_at,
                    response=response,
                    error=exc,
                )
                if isinstance(exc, GenerationProviderError):
                    raise
                raise GenerationProviderError(
                    "El proveedor devolvió una respuesta no utilizable."
                ) from exc

            set_span_attributes(
                span,
                **{
                    "gen_ai.response.model": result.model,
                    "gen_ai.usage.input_tokens": result.usage.input_tokens,
                    "gen_ai.usage.output_tokens": result.usage.output_tokens,
                    "openai.response.id": result.id,
                },
            )
            record_openai_request(
                operation=operation,
                model=result.model,
                outcome="success",
                duration_seconds=perf_counter() - started_at,
                usage=result.usage,
                response=response,
            )
            return result

    def stream(
        self,
        *,
        input_data: ProviderInput,
        instructions: str,
        max_output_tokens: int,
    ) -> Iterator[GenerationStreamEvent]:
        """Normaliza eventos de OpenAI sin exponer sus objetos al cliente HTTP."""

        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            RateLimitError,
        )

        def iterate() -> Iterator[GenerationStreamEvent]:
            operation = "responses.stream"
            started_at = perf_counter()
            text_parts: list[str] = []
            recorded = False
            response_for_id: Any | None = None
            stream: Any | None = None
            headers = openai_request_headers()
            request_options = {"extra_headers": headers} if headers else {}
            # Un generador síncrono puede reanudarse en distintos workers de
            # AnyIO. El span se finaliza explícitamente para no mantener un
            # token de ContextVar abierto entre yields y conservar la traza.
            span = tracer().start_span("openai.responses.stream")
            set_span_attributes(
                span,
                **{
                    "gen_ai.system": "openai",
                    "gen_ai.operation.name": "responses",
                    "gen_ai.request.model": self._model,
                    "gen_ai.request.max_tokens": max_output_tokens,
                    "gen_ai.response.streaming": True,
                },
            )
            try:
                with otel_trace.use_span(span, end_on_exit=False):
                    stream = self._client.responses.create(
                        model=self._model,
                        input=input_data,
                        instructions=instructions,
                        max_output_tokens=max_output_tokens,
                        reasoning={"effort": self._reasoning_effort},
                        text={"verbosity": self._text_verbosity},
                        store=False,
                        stream=True,
                        **request_options,
                    )
                response_for_id = stream
                completed = False
                for event in stream:
                    event_type = str(getattr(event, "type", ""))
                    if event_type == "response.created":
                        response = event.response
                        response_for_id = response
                        yield GenerationStreamStarted(
                            id=str(response.id),
                            model=str(
                                getattr(response, "model", self._model) or self._model
                            ),
                            created_at=int(response.created_at),
                        )
                    elif event_type == "response.output_text.delta":
                        delta = str(getattr(event, "delta", "") or "")
                        if delta:
                            text_parts.append(delta)
                            yield GenerationTextDelta(delta=delta)
                    elif event_type in {
                        "response.completed",
                        "response.incomplete",
                    }:
                        text = "".join(text_parts).strip()
                        if not text:
                            raise GenerationProviderError(
                                "El proveedor terminó el stream sin texto utilizable."
                            )
                        result = _result_from_response(event.response, text=text)
                        response_for_id = event.response
                        set_span_attributes(
                            span,
                            **{
                                "gen_ai.response.model": result.model,
                                "gen_ai.usage.input_tokens": result.usage.input_tokens,
                                "gen_ai.usage.output_tokens": result.usage.output_tokens,
                                "openai.response.id": result.id,
                            },
                        )
                        record_openai_request(
                            operation=operation,
                            model=result.model or self._model,
                            outcome="success",
                            duration_seconds=perf_counter() - started_at,
                            usage=result.usage,
                            response=event.response,
                        )
                        recorded = True
                        completed = True
                        yield GenerationStreamCompleted(result=result)
                    elif event_type == "response.failed":
                        raise GenerationProviderError(
                            "El proveedor no pudo completar el stream."
                        )
                if not completed:
                    raise GenerationProviderError(
                        "El proveedor cerró el stream sin un evento terminal."
                    )
            except GeneratorExit as exc:
                if not recorded:
                    record_openai_request(
                        operation=operation,
                        model=self._model,
                        outcome="disconnected",
                        duration_seconds=perf_counter() - started_at,
                        response=response_for_id,
                        error=exc,
                    )
                    recorded = True
                raise
            except APITimeoutError as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="timeout",
                    duration_seconds=perf_counter() - started_at,
                    response=response_for_id,
                    error=exc,
                )
                recorded = True
                raise GenerationTimeoutError(
                    "El proveedor excedió el tiempo de respuesta."
                ) from exc
            except RateLimitError as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="rate_limit",
                    duration_seconds=perf_counter() - started_at,
                    response=response_for_id,
                    error=exc,
                )
                recorded = True
                raise GenerationRateLimitError(
                    "El proveedor no tiene cuota disponible temporalmente."
                ) from exc
            except (APIConnectionError, APIStatusError) as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="provider_error",
                    duration_seconds=perf_counter() - started_at,
                    response=response_for_id,
                    error=exc,
                )
                recorded = True
                raise GenerationProviderError(
                    "El proveedor de generación no está disponible."
                ) from exc
            except GenerationProviderError as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="invalid_response",
                    duration_seconds=perf_counter() - started_at,
                    response=response_for_id,
                    error=exc,
                )
                recorded = True
                raise
            except Exception as exc:
                mark_span_error(span, exc)
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome="provider_error",
                    duration_seconds=perf_counter() - started_at,
                    response=response_for_id,
                    error=exc,
                )
                recorded = True
                raise GenerationProviderError(
                    "El proveedor devolvió un stream no utilizable."
                ) from exc
            finally:
                try:
                    close = getattr(stream, "close", None)
                    if callable(close):
                        with suppress(Exception):
                            close()
                finally:
                    span.end()

        return iterate()
