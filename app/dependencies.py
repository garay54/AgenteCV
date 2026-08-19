from __future__ import annotations

from functools import lru_cache

from fastapi import HTTPException, status

from app.agent import AgentService
from app.config import get_settings
from app.llm import GenerationConfigurationError, OpenAIResponsesProvider
from app.rag.embeddings import EmbeddingConfigurationError, OpenAIEmbeddingProvider
from app.rag.service import RagService
from app.rag.vector_store import ChromaVectorStore


@lru_cache
def get_agent_service() -> AgentService:
    """Construye una sola vez los adaptadores reutilizables del proceso."""

    settings = get_settings()
    api_key = (
        settings.openai_api_key.get_secret_value()
        if settings.openai_api_key is not None
        else None
    )
    try:
        embeddings = OpenAIEmbeddingProvider(
            api_key=api_key,
            model=settings.openai_embedding_model,
        )
        generation_provider = OpenAIResponsesProvider(
            api_key=api_key,
            model=settings.openai_generation_model,
            reasoning_effort=settings.openai_reasoning_effort,
            text_verbosity=settings.openai_text_verbosity,
            timeout_seconds=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )
    except (EmbeddingConfigurationError, GenerationConfigurationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio no tiene configurado el proveedor de IA.",
        ) from exc
    vector_store = ChromaVectorStore(
        path=settings.chroma_path,
        collection_name=settings.chroma_collection,
    )
    rag_service = RagService(
        settings=settings,
        embedding_provider=embeddings,
        vector_store=vector_store,
    )
    return AgentService(
        rag_service=rag_service,
        generation_provider=generation_provider,
        default_max_output_tokens=settings.generation_max_output_tokens,
    )
