from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Iterable

from .ingest import chunk_pages, read_manual_pages
from .models import DocumentChunk, DocumentRecord, SearchResult
from .storage import JsonStore
from .text import build_tfidf_vectors, cosine_similarity, tfidf_query_vector, tokenize


class DocumentSearchEngine:
    """Hybrid BM25 + TF-IDF search constrained by instrument/model scope."""

    def __init__(self, store_path: str | Path | None = None):
        self.store = JsonStore(store_path) if store_path else None
        self.documents: dict[str, DocumentRecord] = {}
        self.chunks: list[DocumentChunk] = []
        self._tokens: list[list[str]] = []
        self._tfidf_vectors: list[Counter[str]] = []
        self._idf: dict[str, float] = {}
        if self.store:
            self.documents, self.chunks = self.store.load()
        self._rebuild_index()

    def add_document(self, document: DocumentRecord, pages: Iterable[str]) -> None:
        self.documents[document.document_id] = document
        self.chunks = [chunk for chunk in self.chunks if chunk.document_id != document.document_id]
        self.chunks.extend(chunk_pages(document, list(pages)))
        self._rebuild_index()
        self._persist()

    def ingest_file(self, path: str | Path, document_id: str, title: str, instrument: str, model: str | None = None) -> None:
        record = DocumentRecord(document_id=document_id, title=title, instrument=instrument, model=model, source_path=str(path))
        self.add_document(record, read_manual_pages(path))

    def search(
        self,
        query: str,
        *,
        instrument: str | None = None,
        model: str | None = None,
        document_ids: set[str] | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Search only the selected manual scope to avoid model/document mixing."""

        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        query_vec = tfidf_query_vector(query_tokens, self._idf)
        results: list[SearchResult] = []
        avgdl = sum(len(tokens) for tokens in self._tokens) / len(self._tokens) if self._tokens else 1.0
        for idx, chunk in enumerate(self.chunks):
            document = self.documents[chunk.document_id]
            if not self._in_scope(document, instrument, model, document_ids):
                continue
            lexical = self._bm25(query_tokens, self._tokens[idx], avgdl)
            semantic = cosine_similarity(query_vec, self._tfidf_vectors[idx])
            score = (0.65 * lexical) + (0.35 * semantic)
            if score > 0:
                results.append(SearchResult(chunk, document, score, lexical, semantic))
        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    def answer(self, query: str, **scope: object) -> dict[str, object]:
        """Return cited evidence and a conservative status for LLM explanation."""

        results = self.search(query, **scope)
        if not results:
            return {"status": "not_found", "answer": "未在限定文档范围内找到可靠依据。", "citations": []}
        confident = results[0].score >= 0.45 and (len(results) == 1 or results[0].score >= results[1].score * 1.15)
        status = "confident" if confident else "uncertain"
        citations = [{"citation": r.citation, "score": round(r.score, 4), "text": r.chunk.text[:500]} for r in results]
        answer = "找到高相关依据，请结合引用页码核对。" if confident else "结果不够确定，建议在以下文档范围内人工核对。"
        return {"status": status, "answer": answer, "citations": citations}

    def _rebuild_index(self) -> None:
        self._tokens = [tokenize(chunk.text) for chunk in self.chunks]
        self._tfidf_vectors, self._idf = build_tfidf_vectors(self._tokens)

    def _persist(self) -> None:
        if self.store:
            self.store.save(self.documents, self.chunks)

    @staticmethod
    def _in_scope(document: DocumentRecord, instrument: str | None, model: str | None, document_ids: set[str] | None) -> bool:
        if document_ids is not None and document.document_id not in document_ids:
            return False
        if instrument is not None and document.instrument != instrument:
            return False
        if model is not None and document.model != model:
            return False
        return True

    def _bm25(self, query_tokens: list[str], doc_tokens: list[str], avgdl: float, k1: float = 1.5, b: float = 0.75) -> float:
        counts = Counter(doc_tokens)
        score = 0.0
        doc_len = len(doc_tokens) or 1
        for term in query_tokens:
            tf = counts[term]
            if not tf:
                continue
            idf = self._idf.get(term, 1.0)
            denom = tf + k1 * (1 - b + b * doc_len / avgdl)
            score += idf * (tf * (k1 + 1) / denom)
        return score / math.sqrt(len(query_tokens))
