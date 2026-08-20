from __future__ import annotations

from pathlib import Path
from typing import Sequence

from app.rag.models import KnowledgeChunk, SearchResult


class VectorStoreError(RuntimeError):
    """Error controlado del almacén vectorial."""


class ChromaVectorStore:
    def __init__(self, *, path: Path, collection_name: str) -> None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection_name = collection_name

    def _get_or_create_collection(self):
        return self._client.get_or_create_collection(
            name=self._collection_name,
            configuration={"hnsw": {"space": "cosine"}},
            metadata={"purpose": "agente_cv_rag"},
        )

    def rebuild(
        self,
        *,
        chunks: Sequence[KnowledgeChunk],
        embeddings: Sequence[Sequence[float]],
        embedding_model: str,
        corpus_hash: str,
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Cada fragmento debe tener exactamente un embedding.")
        if not chunks:
            raise ValueError("No se puede construir un índice vacío.")

        try:
            self._client.delete_collection(self._collection_name)
        except Exception as exc:
            if "does not exist" not in str(exc).casefold() and "not found" not in str(exc).casefold():
                raise VectorStoreError("No fue posible reemplazar la colección RAG.") from exc

        collection = self._client.get_or_create_collection(
            name=self._collection_name,
            configuration={"hnsw": {"space": "cosine"}},
            metadata={
                "purpose": "agente_cv_rag",
                "embedding_model": embedding_model,
                "corpus_hash": corpus_hash,
            },
        )
        collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=[list(vector) for vector in embeddings],
        )
        return collection.count()

    def count(self) -> int:
        return self._get_or_create_collection().count()

    def search(
        self, query_embedding: Sequence[float], *, n_results: int
    ) -> list[SearchResult]:
        collection = self._get_or_create_collection()
        if collection.count() == 0:
            raise VectorStoreError(
                "El índice RAG está vacío. Ejecuta scripts/build_index.py primero."
            )

        result = collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        ids = result["ids"][0]
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        matches: list[SearchResult] = []
        for chunk_id, document, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=True
        ):
            numeric_distance = float(distance)
            matches.append(
                SearchResult(
                    chunk=KnowledgeChunk(
                        id=chunk_id,
                        text=document,
                        metadata=dict(metadata),
                    ),
                    score=1.0 - numeric_distance,
                    distance=numeric_distance,
                )
            )
        return matches
