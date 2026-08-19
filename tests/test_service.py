from pathlib import Path

from app.config import Settings
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
        documents = ["profile.md", "profile.md", "profile.md", "skills.md", "projects.md"]
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

    results = service.search("perfil")
    documents = [item.chunk.metadata["document"] for item in results]
    assert documents == ["profile.md", "profile.md", "skills.md", "projects.md"]

