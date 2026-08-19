from __future__ import annotations

import hashlib
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from app.rag.models import KnowledgeChunk


INDEXED_DOCUMENTS: dict[str, str] = {
    "profile.md": "perfil",
    "experience.md": "experiencia",
    "projects.md": "proyectos",
    "skills.md": "habilidades",
    "publications.md": "publicaciones",
    "research.md": "investigacion",
}

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_SOURCE_RE = re.compile(r"SRC-[A-Z0-9-]+")


@dataclass(frozen=True, slots=True)
class _Section:
    hierarchy: tuple[str, ...]
    body: str
    source_ids: tuple[str, ...]

    @property
    def group(self) -> tuple[str, ...]:
        return self.hierarchy[:2] if len(self.hierarchy) >= 2 else self.hierarchy


def estimate_tokens(text: str) -> int:
    """Estimación conservadora sin depender del tokenizador del proveedor."""

    return max(1, math.ceil(len(text) / 4))


def _clean_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _extract_sections(markdown: str) -> tuple[str, list[_Section]]:
    hierarchy: list[str] = []
    current_hierarchy: tuple[str, ...] = ()
    current_lines: list[str] = []
    sections: list[_Section] = []
    document_title = "Documento sin título"

    def flush() -> None:
        nonlocal current_lines
        body = "\n".join(current_lines).strip()
        if body and current_hierarchy:
            source_ids = tuple(sorted(set(_SOURCE_RE.findall(body))))
            sections.append(_Section(current_hierarchy, body, source_ids))
        current_lines = []

    for raw_line in markdown.splitlines():
        match = _HEADING_RE.match(raw_line)
        if not match:
            current_lines.append(raw_line)
            continue

        flush()
        level = len(match.group(1))
        heading = _clean_heading(match.group(2))
        if level == 1:
            document_title = heading
        hierarchy = hierarchy[: level - 1]
        while len(hierarchy) < level - 1:
            hierarchy.append(document_title)
        hierarchy.append(heading)
        current_hierarchy = tuple(hierarchy)

    flush()
    return document_title, sections


def _with_inherited_sources(sections: Sequence[_Section]) -> list[_Section]:
    group_sources: dict[tuple[str, ...], set[str]] = defaultdict(set)
    document_sources: set[str] = set()
    for section in sections:
        group_sources[section.group].update(section.source_ids)
        document_sources.update(section.source_ids)

    inherited: list[_Section] = []
    for section in sections:
        sources = set(section.source_ids)
        if not sources:
            sources.update(group_sources[section.group])
        if not sources:
            sources.update(document_sources)
        inherited.append(
            _Section(section.hierarchy, section.body, tuple(sorted(sources)))
        )
    return inherited


def _merge_small_sections(
    sections: Sequence[_Section], min_tokens: int, target_tokens: int
) -> list[_Section]:
    merged: list[_Section] = []
    for section in sections:
        if not merged:
            merged.append(section)
            continue

        previous = merged[-1]
        combined_body = f"{previous.body}\n\n{section.body}"
        same_group = previous.group == section.group
        should_merge = same_group and (
            estimate_tokens(previous.body) < min_tokens
            or estimate_tokens(combined_body) <= target_tokens
        )
        if should_merge and estimate_tokens(combined_body) <= target_tokens:
            labels = tuple(dict.fromkeys((*previous.hierarchy, *section.hierarchy)))
            sources = tuple(sorted(set((*previous.source_ids, *section.source_ids))))
            merged[-1] = _Section(labels, combined_body, sources)
        else:
            merged.append(section)
    return merged


def _tail_words(text: str, approximate_tokens: int) -> str:
    words = text.split()
    count = max(1, int(approximate_tokens * 0.70))
    return " ".join(words[-count:])


def _split_oversized_unit(text: str, max_tokens: int) -> list[str]:
    words = text.split()
    parts: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join((*current, word))
        if current and estimate_tokens(candidate) > max_tokens:
            parts.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        parts.append(" ".join(current))
    return parts


def _split_text(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    if estimate_tokens(text) <= max_tokens:
        return [text]

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    units: list[str] = []
    for paragraph in paragraphs:
        if estimate_tokens(paragraph) <= max_tokens:
            units.append(paragraph)
        else:
            units.extend(_split_oversized_unit(paragraph, max_tokens))

    pieces: list[str] = []
    current = ""
    for unit in units:
        candidate = f"{current}\n\n{unit}".strip()
        if current and estimate_tokens(candidate) > max_tokens:
            pieces.append(current)
            overlap = _tail_words(current, overlap_tokens) if overlap_tokens else ""
            current = f"{overlap}\n\n{unit}".strip()
            if estimate_tokens(current) > max_tokens:
                current = unit
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def _academic_level(section_path: str) -> str:
    normalized = section_path.casefold()
    if "doctor" in normalized:
        return "doctorado"
    if "maestr" in normalized:
        return "maestría"
    return ""


def chunk_markdown_document(
    path: Path,
    *,
    document_type: str,
    min_tokens: int = 150,
    target_tokens: int = 350,
    max_tokens: int = 450,
    overlap_tokens: int = 50,
) -> list[KnowledgeChunk]:
    markdown = path.read_text(encoding="utf-8")
    document_title, raw_sections = _extract_sections(markdown)
    sections = _merge_small_sections(
        _with_inherited_sources(raw_sections), min_tokens, target_tokens
    )

    chunks: list[KnowledgeChunk] = []
    for section in sections:
        section_path = " > ".join(section.hierarchy)
        prefix = f"Documento: {document_title}\nSección: {section_path}\n\n"
        available_tokens = max(50, max_tokens - estimate_tokens(prefix))
        pieces = _split_text(section.body, available_tokens, overlap_tokens)
        for piece_index, piece in enumerate(pieces):
            text = f"{prefix}{piece}".strip()
            fingerprint = "|".join(
                (path.name, section_path, str(piece_index), text)
            ).encode("utf-8")
            chunk_id = hashlib.sha256(fingerprint).hexdigest()[:24]
            chunks.append(
                KnowledgeChunk(
                    id=chunk_id,
                    text=text,
                    metadata={
                        "document": path.name,
                        "document_name": path.name,
                        "document_title": document_title,
                        "document_type": document_type,
                        "section": section.hierarchy[-1],
                        "section_path": section_path,
                        "source_ids": ",".join(section.source_ids),
                        "academic_level": _academic_level(section_path),
                        "chunk_index": len(chunks),
                        "token_estimate": estimate_tokens(text),
                    },
                )
            )
    return chunks


def load_knowledge_corpus(
    knowledge_dir: Path,
    *,
    min_tokens: int = 150,
    target_tokens: int = 350,
    max_tokens: int = 450,
    overlap_tokens: int = 50,
) -> list[KnowledgeChunk]:
    """Carga exclusivamente los documentos autorizados por D04."""

    missing = [name for name in INDEXED_DOCUMENTS if not (knowledge_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(
            "Faltan documentos autorizados del corpus: " + ", ".join(missing)
        )

    chunks: list[KnowledgeChunk] = []
    for name, document_type in INDEXED_DOCUMENTS.items():
        chunks.extend(
            chunk_markdown_document(
                knowledge_dir / name,
                document_type=document_type,
                min_tokens=min_tokens,
                target_tokens=target_tokens,
                max_tokens=max_tokens,
                overlap_tokens=overlap_tokens,
            )
        )
    return chunks


def corpus_fingerprint(chunks: Iterable[KnowledgeChunk]) -> str:
    digest = hashlib.sha256()
    for chunk in sorted(chunks, key=lambda item: item.id):
        digest.update(chunk.id.encode("utf-8"))
        digest.update(chunk.text.encode("utf-8"))
    return digest.hexdigest()
