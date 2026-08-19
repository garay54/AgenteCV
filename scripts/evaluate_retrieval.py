from __future__ import annotations

import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from app.config import PROJECT_ROOT, get_settings
from app.rag.chunking import INDEXED_DOCUMENTS
from app.rag.embeddings import EmbeddingConfigurationError, OpenAIEmbeddingProvider
from app.rag.evaluation import load_retrieval_cases
from app.rag.service import RagService
from app.rag.vector_store import ChromaVectorStore


HIT_AT_3_THRESHOLD = 0.90
TOP_1_THRESHOLD = 0.75


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
    service = RagService(
        settings=settings,
        embedding_provider=provider,
        vector_store=ChromaVectorStore(
            path=settings.chroma_path,
            collection_name=settings.chroma_collection,
        ),
    )
    cases = load_retrieval_cases(settings.knowledge_dir / "question_bank.md")
    details: list[dict[str, object]] = []

    for case in cases:
        started = time.perf_counter()
        error: str | None = None
        try:
            results = service.search(case.query)
        except Exception as exc:
            results = []
            error = f"{type(exc).__name__}: {exc}"
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        documents = [str(item.chunk.metadata["document"]) for item in results]
        hit_at_3 = bool(set(documents[:3]) & set(case.expected_documents))
        top_1 = bool(documents and documents[0] in case.expected_documents)
        excluded_documents = [
            document for document in documents if document not in INDEXED_DOCUMENTS
        ]
        counts = Counter(documents)
        diversity_ok = all(
            count <= settings.rag_max_per_document for count in counts.values()
        )
        details.append(
            {
                "id": case.id,
                "query": case.query,
                "expected_documents": list(case.expected_documents),
                "retrieved": [
                    {
                        "rank": rank,
                        "document": item.chunk.metadata["document"],
                        "section": item.chunk.metadata["section_path"],
                        "source_ids": item.chunk.metadata["source_ids"],
                        "score": round(item.score, 6),
                        "chunk_id": item.chunk.id,
                    }
                    for rank, item in enumerate(results, start=1)
                ],
                "hit_at_3": hit_at_3,
                "top_1": top_1,
                "latency_ms": latency_ms,
                "excluded_documents": excluded_documents,
                "diversity_ok": diversity_ok,
                "error": error,
            }
        )

    total = len(details)
    hit_at_3 = sum(bool(item["hit_at_3"]) for item in details) / total if total else 0
    top_1 = sum(bool(item["top_1"]) for item in details) / total if total else 0
    excluded_count = sum(len(item["excluded_documents"]) for item in details)
    error_count = sum(item["error"] is not None for item in details)
    latency_values = [float(item["latency_ms"]) for item in details]
    passed = (
        hit_at_3 >= HIT_AT_3_THRESHOLD
        and top_1 >= TOP_1_THRESHOLD
        and excluded_count == 0
        and error_count == 0
        and all(bool(item["diversity_ok"]) for item in details)
    )
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evaluation_scope": "Recuperación por documento esperado; la pertinencia de sección requiere revisión del detalle.",
        "embedding_model": provider.model_name,
        "collection": settings.chroma_collection,
        "thresholds": {
            "hit_at_3": HIT_AT_3_THRESHOLD,
            "top_1": TOP_1_THRESHOLD,
            "excluded_documents": 0,
        },
        "summary": {
            "cases": total,
            "hit_at_3": round(hit_at_3, 4),
            "top_1": round(top_1, 4),
            "average_latency_ms": round(sum(latency_values) / total, 2)
            if total
            else 0,
            "max_latency_ms": max(latency_values, default=0),
            "errors": error_count,
            "excluded_documents": excluded_count,
            "passed": passed,
        },
        "cases": details,
    }
    output_dir = PROJECT_ROOT / "artifacts" / "evaluations"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = output_dir / f"retrieval-{timestamp}.json"
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"Reporte: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except EmbeddingConfigurationError as exc:
        raise SystemExit(str(exc)) from exc
