from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from app.rag.chunking import INDEXED_DOCUMENTS
from app.rag.models import SearchResult


@dataclass(frozen=True, slots=True)
class RetrievalCase:
    id: str
    query: str
    expected_documents: tuple[str, ...]
    expected_source_ids: tuple[str, ...]


_FILE_RE = re.compile(r"([a-z_]+\.md)")
_SOURCE_RE = re.compile(r"SRC-[A-Z0-9-]+")


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
            expected_source_ids = tuple(dict.fromkeys(_SOURCE_RE.findall(cells[3])))
            cases.append(
                RetrievalCase(
                    id=case_id,
                    query=query,
                    expected_documents=expected,
                    expected_source_ids=expected_source_ids,
                )
            )
    return cases


def result_matches_case(case: RetrievalCase, result: SearchResult) -> bool:
    """Comprueba documento y trazabilidad, no sólo el nombre del archivo.

    Cuando el caso declara identificadores ``SRC-*``, el fragmento debe
    pertenecer a uno de los documentos aceptados y conservar al menos una de
    esas fuentes. Esto evita considerar correcta, por ejemplo, una sección
    doctoral de ``research.md`` para una pregunta específica de maestría.
    """

    document = str(result.chunk.metadata.get("document", ""))
    if document not in case.expected_documents:
        return False
    if not case.expected_source_ids:
        return True

    raw_source_ids = str(result.chunk.metadata.get("source_ids", ""))
    source_ids = {item.strip() for item in raw_source_ids.split(",") if item.strip()}
    return bool(source_ids.intersection(case.expected_source_ids))


def first_relevant_rank(
    case: RetrievalCase,
    results: Sequence[SearchResult],
    *,
    cutoff: int | None = None,
) -> int | None:
    """Devuelve la primera posición relevante, limitada al corte solicitado."""

    inspected = results if cutoff is None else results[:cutoff]
    for rank, result in enumerate(inspected, start=1):
        if result_matches_case(case, result):
            return rank
    return None
