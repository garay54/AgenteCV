from __future__ import annotations

import re
import unicodedata
from collections import Counter

from app.config import Settings
from app.rag.chunking import corpus_fingerprint, load_knowledge_corpus
from app.rag.embeddings import EmbeddingProvider
from app.rag.models import SearchResult
from app.rag.vector_store import ChromaVectorStore


def _source_count(result: SearchResult) -> int:
    raw_source_ids = str(result.chunk.metadata.get("source_ids", ""))
    return len({item.strip() for item in raw_source_ids.split(",") if item.strip()})


_LEXICAL_STOPWORDS = {
    "a",
    "al",
    "como",
    "cual",
    "de",
    "del",
    "el",
    "en",
    "es",
    "la",
    "las",
    "lo",
    "los",
    "mario",
    "que",
    "se",
    "su",
    "sus",
    "tiene",
    "tuvo",
    "un",
    "una",
    "y",
}


def _lexical_tokens(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return {
        token
        for token in re.findall(r"[a-z0-9]+", ascii_text)
        if len(token) > 1 and token not in _LEXICAL_STOPWORDS
    }


def _lexical_overlap(query: str, text: str) -> float:
    query_tokens = _lexical_tokens(query)
    if not query_tokens:
        return 0.0
    return len(query_tokens.intersection(_lexical_tokens(text))) / len(query_tokens)


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
        # Los encabezados generales heredan varias fuentes y pueden desplazar a
        # fragmentos específicos por diferencias mínimas de similitud. También
        # interesa conservar coincidencias literales de títulos, revistas y
        # tecnologías. El reranking combina una penalización pequeña por amplitud
        # de fuentes con un bono léxico acotado sobre los candidatos vectoriales.
        # El score coseno original se conserva para diagnóstico y umbrales.
        candidates = sorted(
            candidates,
            key=lambda item: item.score
            - self.settings.rag_source_breadth_penalty
            * max(0, _source_count(item) - 1)
            + self.settings.rag_lexical_bonus
            * _lexical_overlap(query, item.chunk.text),
            reverse=True,
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
