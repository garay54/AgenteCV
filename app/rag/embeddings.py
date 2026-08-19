from __future__ import annotations

from typing import Protocol, Sequence


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
            response = self._client.embeddings.create(model=self._model, input=batch)
            ordered = sorted(response.data, key=lambda item: item.index)
            embeddings.extend([list(item.embedding) for item in ordered])
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=self._model, input=[text])
        return list(response.data[0].embedding)

