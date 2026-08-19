from __future__ import annotations

from app.config import get_settings
from app.rag.embeddings import EmbeddingConfigurationError, OpenAIEmbeddingProvider
from app.rag.service import RagService
from app.rag.vector_store import ChromaVectorStore


def main() -> None:
    """Reutiliza el índice persistente o lo crea antes de arrancar la API."""

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
    current_count = store.count()
    if current_count > 0:
        print(f"Índice RAG disponible: {current_count} fragmentos")
        return

    count = RagService(
        settings=settings,
        embedding_provider=provider,
        vector_store=store,
    ).rebuild_index()
    print(f"Índice RAG construido: {count} fragmentos")


if __name__ == "__main__":
    try:
        main()
    except EmbeddingConfigurationError as exc:
        raise SystemExit(str(exc)) from exc
