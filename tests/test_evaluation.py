from pathlib import Path

from app.rag.evaluation import (
    RetrievalCase,
    first_relevant_rank,
    load_retrieval_cases,
    result_matches_case,
)
from app.rag.models import KnowledgeChunk, SearchResult


def test_question_bank_exposes_reproducible_retrieval_cases() -> None:
    path = Path(__file__).resolve().parents[1] / "knowledge" / "question_bank.md"
    cases = load_retrieval_cases(path)

    assert len(cases) >= 40
    assert all(case.expected_documents for case in cases)
    assert all(case.expected_source_ids for case in cases)
    assert not any(case.id in {"QB-45", "QB-50", "QB-51"} for case in cases)


def _result(document: str, source_ids: str) -> SearchResult:
    return SearchResult(
        chunk=KnowledgeChunk(
            id=f"{document}:{source_ids}",
            text="fragmento",
            metadata={"document": document, "source_ids": source_ids},
        ),
        score=0.8,
        distance=0.2,
    )


def test_relevance_requires_an_allowed_document_and_matching_source() -> None:
    case = RetrievalCase(
        id="QB-X",
        query="¿De qué trató la tesis de maestría?",
        expected_documents=("projects.md", "research.md"),
        expected_source_ids=("SRC-MSC-THESIS-01",),
    )

    assert not result_matches_case(
        case, _result("research.md", "SRC-PHD-THESIS-01")
    )
    assert not result_matches_case(
        case, _result("profile.md", "SRC-MSC-THESIS-01")
    )
    assert result_matches_case(
        case, _result("research.md", "SRC-MSC-THESIS-01")
    )


def test_first_relevant_rank_respects_cutoff() -> None:
    case = RetrievalCase(
        id="QB-X",
        query="pregunta",
        expected_documents=("skills.md",),
        expected_source_ids=("SRC-CV-01",),
    )
    results = [
        _result("profile.md", "SRC-CV-01"),
        _result("experience.md", "SRC-CV-01"),
        _result("projects.md", "SRC-PHD-THESIS-01"),
        _result("skills.md", "SRC-CV-01"),
    ]

    assert first_relevant_rank(case, results, cutoff=3) is None
    assert first_relevant_rank(case, results, cutoff=4) == 4
