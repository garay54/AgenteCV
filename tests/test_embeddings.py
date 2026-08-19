import pytest

from app.rag.embeddings import EmbeddingConfigurationError, OpenAIEmbeddingProvider


def test_openai_provider_requires_api_key_without_exposing_a_secret() -> None:
    with pytest.raises(EmbeddingConfigurationError, match="OPENAI_API_KEY"):
        OpenAIEmbeddingProvider(api_key=None)
