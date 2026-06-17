from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentRecord:
    """Metadata for an instrument manual uploaded by an administrator."""

    document_id: str
    title: str
    instrument: str
    model: str | None = None
    revision: str | None = None
    source_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentChunk:
    """Searchable page-level or section-level text with citation data."""

    chunk_id: str
    document_id: str
    page_start: int
    page_end: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    """Ranked retrieval result with enough metadata to cite the source."""

    chunk: DocumentChunk
    document: DocumentRecord
    score: float
    lexical_score: float
    semantic_score: float

    @property
    def citation(self) -> str:
        page = f"p.{self.chunk.page_start}" if self.chunk.page_start == self.chunk.page_end else f"pp.{self.chunk.page_start}-{self.chunk.page_end}"
        return f"{self.document.title}, {page}"
