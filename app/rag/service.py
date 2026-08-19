from __future__ import annotations

from collections import Counter

from app.config import Settings
from app.rag.chunking import corpus_fingerprint, load_knowledge_corpus
from app.rag.embeddings import EmbeddingProvider
from app.rag.models import SearchResult
from app.rag.vector_store import ChromaVectorStore


class RagService:
    def __init__(
        self,
        *,
        settings: Settings,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
    ) -> None:
        self.settings = settings
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def rebuild_index(self) -> int:
        chunks = load_knowledge_corpus(
            self.settings.knowledge_dir,
            min_tokens=self.settings.rag_chunk_min_tokens,
            target_tokens=self.settings.rag_chunk_target_tokens,
            max_tokens=self.settings.rag_chunk_max_tokens,
            overlap_tokens=self.settings.rag_chunk_overlap_tokens,
        )
        embeddings = self.embedding_provider.embed_documents(
            [chunk.text for chunk in chunks]
        )
        return self.vector_store.rebuild(
            chunks=chunks,
            embeddings=embeddings,
            embedding_model=self.embedding_provider.model_name,
            corpus_hash=corpus_fingerprint(chunks),
        )

    def search(self, query: str) -> list[SearchResult]:
        candidates = self.vector_store.search(
            self.embedding_provider.embed_query(query),
            n_results=self.settings.rag_candidate_k,
        )
        selected: list[SearchResult] = []
        per_document: Counter[str] = Counter()
        for candidate in candidates:
            if (
                self.settings.rag_min_score is not None
                and candidate.score < self.settings.rag_min_score
            ):
                continue
            document = str(candidate.chunk.metadata["document"])
            if per_document[document] >= self.settings.rag_max_per_document:
                continue
            selected.append(candidate)
            per_document[document] += 1
            if len(selected) >= self.settings.rag_top_k:
                break
        return selected

