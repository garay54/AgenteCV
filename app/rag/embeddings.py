from __future__ import annotations

from collections.abc import Sequence
from time import perf_counter
from typing import Protocol

from app.llm import GenerationUsage
from app.observability import (
    mark_span_error,
    openai_request_headers,
    record_openai_request,
    set_span_attributes,
    tracer,
)


class EmbeddingConfigurationError(RuntimeError):
    """La configuración no permite utilizar el proveedor de embeddings."""


class EmbeddingProvider(Protocol):
    @property
    def model_name(self) -> str: ...

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str = "text-embedding-3-small",
        batch_size: int = 100,
    ) -> None:
        if not api_key:
            raise EmbeddingConfigurationError(
                "Falta OPENAI_API_KEY. Agrégala únicamente a .env antes de construir el índice."
            )
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._batch_size = batch_size

    @property
    def model_name(self) -> str:
        return self._model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = list(texts[start : start + self._batch_size])
            response = self._create_embeddings(
                batch,
                operation="embeddings.documents",
            )
            ordered = sorted(response.data, key=lambda item: item.index)
            embeddings.extend([list(item.embedding) for item in ordered])
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self._create_embeddings(
            [text],
            operation="embeddings.query",
        )
        return list(response.data[0].embedding)

    def _create_embeddings(self, inputs: list[str], *, operation: str):
        started_at = perf_counter()
        headers = openai_request_headers()
        request_options = {"extra_headers": headers} if headers else {}
        with tracer().start_as_current_span("openai.embeddings.create") as span:
            set_span_attributes(
                span,
                **{
                    "gen_ai.system": "openai",
                    "gen_ai.operation.name": "embeddings",
                    "gen_ai.request.model": self._model,
                    "gen_ai.request.input_count": len(inputs),
                },
            )
            try:
                response = self._client.embeddings.create(
                    model=self._model,
                    input=inputs,
                    **request_options,
                )
            except Exception as exc:
                mark_span_error(span, exc)
                error_name = type(exc).__name__.casefold()
                if "ratelimit" in error_name:
                    outcome = "rate_limit"
                elif "timeout" in error_name:
                    outcome = "timeout"
                else:
                    outcome = "provider_error"
                record_openai_request(
                    operation=operation,
                    model=self._model,
                    outcome=outcome,
                    duration_seconds=perf_counter() - started_at,
                    error=exc,
                )
                raise

            raw_usage = getattr(response, "usage", None)
            input_tokens = int(
                getattr(raw_usage, "prompt_tokens", 0)
                or getattr(raw_usage, "input_tokens", 0)
                or 0
            )
            total_tokens = int(getattr(raw_usage, "total_tokens", 0) or input_tokens)
            usage = GenerationUsage(
                input_tokens=input_tokens,
                total_tokens=total_tokens,
            )
            set_span_attributes(
                span,
                **{
                    "gen_ai.usage.input_tokens": usage.input_tokens,
                    "gen_ai.response.model": self._model,
                },
            )
            record_openai_request(
                operation=operation,
                model=self._model,
                outcome="success",
                duration_seconds=perf_counter() - started_at,
                usage=usage,
                response=response,
            )
            return response
