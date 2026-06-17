from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import DocumentChunk, DocumentRecord


class JsonStore:
    """Simple local JSON store suitable for prototypes and offline deployments."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, documents: dict[str, DocumentRecord], chunks: list[DocumentChunk]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "documents": [doc.__dict__ for doc in documents.values()],
            "chunks": [chunk.__dict__ for chunk in chunks],
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> tuple[dict[str, DocumentRecord], list[DocumentChunk]]:
        if not self.path.exists():
            return {}, []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        documents = {item["document_id"]: DocumentRecord(**item) for item in payload.get("documents", [])}
        chunks = [DocumentChunk(**item) for item in payload.get("chunks", [])]
        return documents, chunks
