from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.rag.chunking import INDEXED_DOCUMENTS


@dataclass(frozen=True, slots=True)
class RetrievalCase:
    id: str
    query: str
    expected_documents: tuple[str, ...]


_FILE_RE = re.compile(r"([a-z_]+\.md)")


def load_retrieval_cases(path: Path) -> list[RetrievalCase]:
    cases: list[RetrievalCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `QB-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        case_id = cells[0].strip("`")
        query = cells[1]
        expected = tuple(
            dict.fromkeys(
                name
                for name in _FILE_RE.findall(cells[3])
                if name in INDEXED_DOCUMENTS
            )
        )
        if expected:
            cases.append(RetrievalCase(case_id, query, expected))
    return cases

