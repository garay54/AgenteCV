from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol


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


def _integer_attribute(value: Any, name: str) -> int:
    raw = getattr(value, name, 0) if value is not None else 0
    return int(raw or 0)


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
        from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

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
            )
        except APITimeoutError as exc:
            raise GenerationTimeoutError(
                "El proveedor excedió el tiempo de respuesta."
            ) from exc
        except RateLimitError as exc:
            raise GenerationRateLimitError(
                "El proveedor no tiene cuota disponible temporalmente."
            ) from exc
        except (APIConnectionError, APIStatusError) as exc:
            raise GenerationProviderError(
                "El proveedor de generación no está disponible."
            ) from exc

        text = str(getattr(response, "output_text", "") or "").strip()
        if not text:
            raise GenerationProviderError(
                "El proveedor terminó la solicitud sin texto utilizable."
            )

        usage = getattr(response, "usage", None)
        input_details = getattr(usage, "input_tokens_details", None)
        output_details = getattr(usage, "output_tokens_details", None)
        incomplete_details = getattr(response, "incomplete_details", None)

        return GenerationResult(
            id=str(response.id),
            text=text,
            model=str(getattr(response, "model", self._model) or self._model),
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
                reasoning_tokens=_integer_attribute(
                    output_details, "reasoning_tokens"
                ),
            ),
        )
