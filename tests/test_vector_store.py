from pathlib import Path

from app.rag.models import KnowledgeChunk
from app.rag.vector_store import ChromaVectorStore


def test_chroma_rebuild_and_cosine_search(tmp_path: Path) -> None:
    store = ChromaVectorStore(path=tmp_path / "chroma", collection_name="test_collection")
    chunks = [
        KnowledgeChunk("a", "experiencia python", {"document": "skills.md", "section": "Python"}),
        KnowledgeChunk("b", "publicaciones", {"document": "publications.md", "section": "Artículos"}),
    ]
    count = store.rebuild(
        chunks=chunks,
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        embedding_model="test",
        corpus_hash="abc",
    )

    assert count == 2
    results = store.search([1.0, 0.0], n_results=2)
    assert results[0].chunk.id == "a"
    assert results[0].score > results[1].score

