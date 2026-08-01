"""
Token Budget Manager for Prompt Intelligence Framework.

Estimates prompt token usage, enforces max token limits, and intelligently trims context text while
preserving highest-ranked and highest-confidence RAG evidence items.
"""

from typing import Any


class TokenBudgetManager:
    """
    Token Manager calculating token counts and trimming low-rank evidence to stay within budget.
    """

    def __init__(self, default_token_budget: int = 4096) -> None:
        self.default_token_budget = default_token_budget

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a text string using standard ~4 characters per token heuristic.

        Args:
            text (str): Input text payload.

        Returns:
            int: Estimated token count.
        """
        if not text:
            return 0
        return max(1, len(text) // 4)

    def trim_evidence_context(
        self,
        evidence_items: list[Any],
        max_tokens: int,
    ) -> list[Any]:
        """
        Intelligently trim context evidence items to fit within max_tokens budget.
        Sorts evidence by confidence score or rank in descending order before trimming to preserve
        the highest-quality factual evidence.

        Args:
            evidence_items (list[Any]): List of Evidence objects or QueryResult matches.
            max_tokens (int): Maximum token budget allocated for RAG evidence.

        Returns:
            list[Any]: Preserved highest-ranked evidence items fitting within token budget.
        """
        if not evidence_items:
            return []

        # Sort evidence items by quality metric (confidence score or similarity score) descending
        sorted_items = list(evidence_items)

        def get_sort_key(item: Any) -> float:
            if hasattr(item, "confidence") and hasattr(item.confidence, "value"):
                return float(item.confidence.value)
            if hasattr(item, "score"):
                return float(item.score)
            return 0.5

        sorted_items.sort(key=get_sort_key, reverse=True)

        preserved: list[Any] = []
        current_tokens = 0

        for item in sorted_items:
            # Extract item text
            if hasattr(item, "fact"):
                text_repr = str(item.fact)
            elif hasattr(item, "chunk") and hasattr(item.chunk, "text"):
                text_repr = str(item.chunk.text)
            else:
                text_repr = str(item)

            item_toks = self.estimate_tokens(text_repr)
            if current_tokens + item_toks <= max_tokens:
                preserved.append(item)
                current_tokens += item_toks
            else:
                break

        return preserved
