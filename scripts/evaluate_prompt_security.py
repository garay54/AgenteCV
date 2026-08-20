from __future__ import annotations

import json
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from app.config import PROJECT_ROOT
from app.dependencies import get_agent_service
from app.models import ResponseCreateRequest


CASES_PATH = PROJECT_ROOT / "knowledge" / "prompt_security_cases.json"
REPORT_DIR = PROJECT_ROOT / "artifacts" / "evaluations"


def _normalized(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


def _load_cases(path: Path = CASES_PATH) -> list[dict[str, object]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("El corpus de seguridad debe ser una lista JSON.")
    return raw


def _evaluate_case(case: dict[str, object], response: str) -> dict[str, object]:
    normalized_response = _normalized(response)
    required = [
        _normalized(str(item)) for item in case.get("required_any", [])
    ]
    forbidden = [
        _normalized(str(item)) for item in case.get("forbidden_any", [])
    ]
    required_match = next(
        (item for item in required if item in normalized_response),
        None,
    )
    forbidden_hits = [
        item for item in forbidden if item in normalized_response
    ]
    return {
        "passed": required_match is not None and not forbidden_hits,
        "required_match": required_match,
        "forbidden_hits": forbidden_hits,
    }


def main() -> None:
    service = get_agent_service()
    details: list[dict[str, object]] = []

    for case in _load_cases():
        started = time.perf_counter()
        error: str | None = None
        response_text = ""
        try:
            request = ResponseCreateRequest.model_validate(case["request"])
            response_text = service.answer(request).generation.text
            result = _evaluate_case(case, response_text)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            result = {
                "passed": False,
                "required_match": None,
                "forbidden_hits": [],
            }

        details.append(
            {
                "id": case["id"],
                "category": case["category"],
                "passed": result["passed"],
                "required_match": result["required_match"],
                "forbidden_hits": result["forbidden_hits"],
                "response": response_text,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "error": error,
            }
        )

    passed = sum(bool(item["passed"]) for item in details)
    generated_at = datetime.now(timezone.utc)
    report = {
        "generated_at": generated_at.isoformat(),
        "method": (
            "Heurística reproducible por marcadores prohibidos y expresiones de "
            "rechazo; complementa, pero no sustituye, revisión humana."
        ),
        "total": len(details),
        "passed": passed,
        "failed": len(details) - passed,
        "pass_rate": passed / len(details) if details else 0.0,
        "details": details,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / (
        f"prompt-security-{generated_at.strftime('%Y%m%d-%H%M%S')}.json"
    )
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        f"Prompt security: {passed}/{len(details)} casos aprobados. "
        f"Reporte: {report_path}"
    )
    if passed != len(details):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
