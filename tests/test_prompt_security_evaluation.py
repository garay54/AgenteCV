import json
from pathlib import Path

from app.models import ResponseCreateRequest


def test_prompt_security_corpus_is_complete_and_valid() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "knowledge"
        / "prompt_security_cases.json"
    )
    cases = json.loads(path.read_text(encoding="utf-8"))

    assert len(cases) >= 5
    assert len({case["id"] for case in cases}) == len(cases)
    assert {
        "direct_prompt_injection",
        "prompt_extraction",
        "client_instructions",
        "forged_history",
        "scope_bypass",
    } <= {case["category"] for case in cases}
    assert all(case["required_any"] for case in cases)
    assert all(case["forbidden_any"] for case in cases)
    assert all(
        ResponseCreateRequest.model_validate(case["request"])
        for case in cases
    )
