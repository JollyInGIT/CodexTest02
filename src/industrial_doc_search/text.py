from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable

_TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_\-\.]*|[\u4e00-\u9fff]", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Tokenize model names as terms and CJK text as searchable characters."""

    return [token.lower() for token in _TOKEN_RE.findall(text)]


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    common = set(left) & set(right)
    numerator = sum(left[t] * right[t] for t in common)
    left_norm = math.sqrt(sum(v * v for v in left.values()))
    right_norm = math.sqrt(sum(v * v for v in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def build_tfidf_vectors(tokenized_docs: Iterable[list[str]]) -> tuple[list[Counter[str]], dict[str, float]]:
    docs = list(tokenized_docs)
    doc_count = len(docs)
    df: Counter[str] = Counter()
    for tokens in docs:
        df.update(set(tokens))
    idf = {term: math.log((doc_count + 1) / (freq + 1)) + 1 for term, freq in df.items()}
    vectors: list[Counter[str]] = []
    for tokens in docs:
        tf = Counter(tokens)
        vectors.append(Counter({term: count * idf[term] for term, count in tf.items()}))
    return vectors, idf


def tfidf_query_vector(query_tokens: list[str], idf: dict[str, float]) -> Counter[str]:
    tf = Counter(query_tokens)
    return Counter({term: count * idf.get(term, 1.0) for term, count in tf.items()})
