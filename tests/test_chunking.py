from pathlib import Path

from app.rag.chunking import (
    INDEXED_DOCUMENTS,
    chunk_markdown_document,
    load_knowledge_corpus,
)


def test_heading_metadata_source_inheritance_and_stable_ids(tmp_path: Path) -> None:
    source = tmp_path / "sample.md"
    source.write_text(
        """# Perfil de prueba

## Proyecto doctoral

Contexto confirmado. `[SRC-TEST-01]`

### Resultado

Resultado medible y verificable.
""",
        encoding="utf-8",
    )
    first = chunk_markdown_document(source, document_type="prueba")
    second = chunk_markdown_document(source, document_type="prueba")

    assert [chunk.id for chunk in first] == [chunk.id for chunk in second]
    assert all(chunk.metadata["document"] == "sample.md" for chunk in first)
    assert all("SRC-TEST-01" in chunk.metadata["source_ids"] for chunk in first)
    assert all("Proyecto doctoral" in chunk.metadata["section_path"] for chunk in first)


def test_does_not_merge_different_h2_groups(tmp_path: Path) -> None:
    source = tmp_path / "sample.md"
    source.write_text(
        """# Proyectos

## Proyecto uno

Texto uno. `[SRC-ONE]`

## Proyecto dos

Texto dos. `[SRC-TWO]`
""",
        encoding="utf-8",
    )
    chunks = chunk_markdown_document(
        source, document_type="proyectos", min_tokens=1000, target_tokens=1000
    )
    assert len(chunks) == 2
    assert not any("Proyecto uno" in item.text and "Proyecto dos" in item.text for item in chunks)


def test_live_corpus_uses_only_allowlisted_documents() -> None:
    knowledge_dir = Path(__file__).resolve().parents[1] / "knowledge"
    chunks = load_knowledge_corpus(knowledge_dir)
    indexed = {str(chunk.metadata["document"]) for chunk in chunks}

    assert indexed == set(INDEXED_DOCUMENTS)
    assert "faq.md" not in indexed
    assert "open_questions.md" not in indexed
    assert "question_bank.md" not in indexed
    assert all(chunk.metadata["section_path"] for chunk in chunks)
    assert all(chunk.metadata["source_ids"] for chunk in chunks)
    assert all(int(chunk.metadata["token_estimate"]) <= 450 for chunk in chunks)

