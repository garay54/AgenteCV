from __future__ import annotations

from app.config import get_settings
from app.rag.embeddings import EmbeddingConfigurationError, OpenAIEmbeddingProvider
from app.rag.service import RagService
from app.rag.vector_store import ChromaVectorStore


def main() -> None:
    settings = get_settings()
    api_key = (
        settings.openai_api_key.get_secret_value()
        if settings.openai_api_key is not None
        else None
    )
    provider = OpenAIEmbeddingProvider(
        api_key=api_key,
        model=settings.openai_embedding_model,
    )
    store = ChromaVectorStore(
        path=settings.chroma_path,
        collection_name=settings.chroma_collection,
    )
    count = RagService(
        settings=settings,
        embedding_provider=provider,
        vector_store=store,
    ).rebuild_index()
    print(f"Índice construido: {count} fragmentos")
    print(f"Modelo de embeddings: {provider.model_name}")
    print(f"Colección: {settings.chroma_collection}")


if __name__ == "__main__":
    try:
        main()
    except EmbeddingConfigurationError as exc:
        raise SystemExit(str(exc)) from exc
