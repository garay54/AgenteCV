from pathlib import Path

from app.rag.evaluation import load_retrieval_cases


def test_question_bank_exposes_reproducible_retrieval_cases() -> None:
    path = Path(__file__).resolve().parents[1] / "knowledge" / "question_bank.md"
    cases = load_retrieval_cases(path)

    assert len(cases) >= 40
    assert all(case.expected_documents for case in cases)
    assert not any(case.id in {"QB-45", "QB-50", "QB-51"} for case in cases)

