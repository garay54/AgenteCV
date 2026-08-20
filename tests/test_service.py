from pathlib import Path

from app.config import Settings
from app.observability import RAG_SEARCHES
from app.rag.models import KnowledgeChunk, SearchResult
from app.rag.service import RagService


class _EmbeddingStub:
    model_name = "stub"

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0]

    def embed_documents(self, texts):
        return [[1.0, 0.0] for _ in texts]


class _StoreStub:
    def search(self, query_embedding, *, n_results: int):
        documents = [
            "profile.md",
            "profile.md",
            "profile.md",
            "skills.md",
            "projects.md",
        ]
        return [
            SearchResult(
                chunk=KnowledgeChunk(
                    id=str(index),
                    text=document,
                    metadata={"document": document},
                ),
                score=1 - index / 10,
                distance=index / 10,
            )
            for index, document in enumerate(documents)
        ]


class _SourceBreadthStoreStub:
    def search(self, query_embedding, *, n_results: int):
        return [
            SearchResult(
                chunk=KnowledgeChunk(
                    id="generic",
                    text="encabezado general",
                    metadata={
                        "document": "publications.md",
                        "source_ids": "SRC-A,SRC-B,SRC-C",
                    },
                ),
                score=0.800,
                distance=0.200,
            ),
            SearchResult(
                chunk=KnowledgeChunk(
                    id="specific",
                    text="publicación específica",
                    metadata={
                        "document": "publications.md",
                        "source_ids": "SRC-B",
                    },
                ),
                score=0.795,
                distance=0.205,
            ),
        ]


class _LexicalStoreStub:
    def search(self, query_embedding, *, n_results: int):
        return [
            SearchResult(
                chunk=KnowledgeChunk(
                    id="semantic-generic",
                    text="Contribución académica general.",
                    metadata={"document": "research.md", "source_ids": "SRC-A"},
                ),
                score=0.500,
                distance=0.500,
            ),
            SearchResult(
                chunk=KnowledgeChunk(
                    id="literal-specific",
                    text="Artículo de CIENCIA ergo-sum: contribución individual documentada.",
                    metadata={
                        "document": "publications.md",
                        "source_ids": "SRC-B",
                    },
                ),
                score=0.470,
                distance=0.530,
            ),
        ]


def test_search_applies_top_k_and_document_diversity(tmp_path: Path) -> None:
    settings = Settings(
        knowledge_dir=tmp_path,
        chroma_path=tmp_path / "chroma",
        rag_top_k=4,
        rag_candidate_k=10,
        rag_max_per_document=2,
    )
    service = RagService(
        settings=settings,
        embedding_provider=_EmbeddingStub(),
        vector_store=_StoreStub(),
    )

    searches_before = float(RAG_SEARCHES.labels(outcome="success")._value.get())
    results = service.search("perfil")
    documents = [item.chunk.metadata["document"] for item in results]
    assert documents == ["profile.md", "profile.md", "skills.md", "projects.md"]
    assert (
        float(RAG_SEARCHES.labels(outcome="success")._value.get())
        == searches_before + 1
    )


def test_search_prefers_specific_source_over_generic_heading(tmp_path: Path) -> None:
    settings = Settings(
        knowledge_dir=tmp_path,
        chroma_path=tmp_path / "chroma",
        rag_top_k=2,
        rag_candidate_k=10,
        rag_max_per_document=2,
        rag_source_breadth_penalty=0.005,
    )
    service = RagService(
        settings=settings,
        embedding_provider=_EmbeddingStub(),
        vector_store=_SourceBreadthStoreStub(),
    )

    results = service.search("artículo")

    assert [item.chunk.id for item in results] == ["specific", "generic"]
    assert results[0].score == 0.795


def test_search_uses_lexical_aliases_to_rerank_vector_candidates(
    tmp_path: Path,
) -> None:
    settings = Settings(
        knowledge_dir=tmp_path,
        chroma_path=tmp_path / "chroma",
        rag_top_k=2,
        rag_candidate_k=10,
        rag_max_per_document=2,
        rag_source_breadth_penalty=0.0,
        rag_lexical_bonus=0.05,
    )
    service = RagService(
        settings=settings,
        embedding_provider=_EmbeddingStub(),
        vector_store=_LexicalStoreStub(),
    )

    results = service.search(
        "¿Qué contribución individual tuvo en el artículo de CIENCIA ergo-sum?"
    )

    assert [item.chunk.id for item in results] == [
        "literal-specific",
        "semantic-generic",
    ]
