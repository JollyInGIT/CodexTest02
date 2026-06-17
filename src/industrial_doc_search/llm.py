from __future__ import annotations

from .models import SearchResult


class CitationPromptBuilder:
    """Builds grounded prompts; callers may send them to an approved LLM."""

    @staticmethod
    def build(query: str, results: list[SearchResult]) -> str:
        evidence = "\n\n".join(
            f"[{idx}] {result.citation}\n{result.chunk.text}"
            for idx, result in enumerate(results, start=1)
        )
        return (
            "你是工业仪器文档检索助手。只能依据给定证据回答；"
            "若证据不足，说明不确定并列出需要人工核对的文档页码。\n"
            f"问题：{query}\n\n证据：\n{evidence}\n\n回答时必须引用证据编号。"
        )
