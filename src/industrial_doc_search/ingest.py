from __future__ import annotations

from pathlib import Path

from .models import DocumentChunk, DocumentRecord


def read_manual_pages(path: str | Path) -> list[str]:
    """Read a PDF or text manual into page strings.

    Text files can use form-feed characters to mark page breaks. PDF support is
    optional so the core search engine remains installable in restricted plants.
    """

    path = Path(path)
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return [(page.extract_text() or "") for page in reader.pages]
    text = path.read_text(encoding="utf-8")
    return text.split("\f") if "\f" in text else [text]


def chunk_pages(document: DocumentRecord, pages: list[str], pages_per_chunk: int = 1) -> list[DocumentChunk]:
    """Create citation-preserving chunks without crossing document boundaries."""

    chunks: list[DocumentChunk] = []
    for start in range(0, len(pages), pages_per_chunk):
        page_text = "\n".join(pages[start : start + pages_per_chunk]).strip()
        if not page_text:
            continue
        page_start = start + 1
        page_end = min(start + pages_per_chunk, len(pages))
        chunks.append(
            DocumentChunk(
                chunk_id=f"{document.document_id}:p{page_start}-{page_end}",
                document_id=document.document_id,
                page_start=page_start,
                page_end=page_end,
                text=page_text,
                metadata={"instrument": document.instrument, "model": document.model},
            )
        )
    return chunks
