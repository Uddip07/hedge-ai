"""
Context Builder for Prompt Intelligence Framework.

Formats and assembles Agent Context, RAG Evidence items, Market Data quotes, and User Requests into structured text blocks.
"""

from typing import Any

from packages.ai.models.agent_context import AgentContext


class ContextBuilder:
    """
    Builder formatting runtime environment components into clean markdown prompt context blocks.
    """

    def format_market_data(self, market_data: Any | None) -> str:
        """Format market price quote or market status into markdown text."""
        if market_data is None:
            return "No live market data available."
        if isinstance(market_data, dict):
            lines = [f"- {k}: {v}" for k, v in market_data.items()]
            return "\n".join(lines)
        if hasattr(market_data, "to_dict"):
            d = market_data.to_dict()
            lines = [f"- {k}: {v}" for k, v in d.items()]
            return "\n".join(lines)
        return str(market_data)

    def format_rag_evidence(self, evidence_list: list[Any] | None) -> str:
        """Format list of RAG evidence items or QueryResult matches into markdown text."""
        if not evidence_list:
            return "No RAG evidence documents retrieved."

        formatted_lines: list[str] = []
        for idx, item in enumerate(evidence_list, start=1):
            if hasattr(item, "fact"):
                conf_val = item.confidence.value if hasattr(item, "confidence") else "0.8"
                formatted_lines.append(f"{idx}. Fact: {item.fact} (Confidence: {conf_val})")
            elif hasattr(item, "chunk") and hasattr(item.chunk, "text"):
                score_val = getattr(item, "score", 0.8)
                formatted_lines.append(
                    f"{idx}. Match: {item.chunk.text} (Relevance Score: {score_val:.2f})"
                )
            else:
                formatted_lines.append(f"{idx}. {str(item)}")

        return "\n".join(formatted_lines)

    def build_full_context(
        self,
        agent_context: AgentContext,
        market_data: Any | None = None,
        rag_evidence: list[Any] | None = None,
        user_request: str | None = None,
    ) -> dict[str, str]:
        """
        Build runtime variable dictionary map for prompt rendering.

        Returns:
            dict[str, str]: Variable substitution map (ticker, market_data, rag_evidence, user_request).
        """
        ticker_str = agent_context.ticker.full_symbol
        market_str = self.format_market_data(market_data)
        evidence_str = self.format_rag_evidence(rag_evidence)
        req_str = user_request or f"Analyze investment thesis for {ticker_str}."

        return {
            "ticker": ticker_str,
            "market_data": market_str,
            "rag_evidence": evidence_str,
            "user_request": req_str,
        }
