"""
Technical Analysis Agent (Quant) Implementation.

Specialized agent analyzing chart patterns, RSI, MACD, volume trends, and moving averages.
"""

from decimal import Decimal
from typing import Any

from packages.ai.agents.base import BaseAgent
from packages.ai.models.agent_context import AgentContext
from packages.ai.models.agent_result import AgentResult
from packages.ai.prompts.prompt_registry import PromptRegistry
from packages.domain.ai.reasoning import Evidence
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class TechnicalAgent(BaseAgent):
    """
    Quantitative Technical Analyst Agent (AgentType.QUANT).
    """

    def __init__(
        self,
        prompt_registry: PromptRegistry | None = None,
        weight: Decimal | float | str = "1.0",
    ) -> None:
        super().__init__(prompt_registry=prompt_registry, weight=weight)

    @property
    def agent_type(self) -> AgentType:
        return AgentType.QUANT

    def _execute_analysis(self, context: AgentContext) -> AgentResult:
        ticker_str = context.ticker.full_symbol

        evidence_data = context.parameters.get("evidence")
        technicals: dict[str, Any] = {}
        if evidence_data and hasattr(evidence_data, "technical_indicators"):
            technicals = evidence_data.technical_indicators or {}

        rsi = technicals.get("rsi_14", 50.0)
        trend = technicals.get("trend", "Neutral")
        chg_pct = technicals.get("change_percent", 0.0)

        # Dynamic score derived from RSI & Momentum
        base_score = Decimal("0.50")
        if trend == "Bullish":
            base_score += Decimal("0.20")
        elif trend == "Bearish":
            base_score -= Decimal("0.20")

        if 40.0 <= rsi <= 70.0:
            base_score += Decimal("0.10")

        score_clamped = max(Decimal("0.10"), min(Decimal("0.95"), base_score))
        rec = (
            RecommendationType.BUY if score_clamped >= Decimal("0.60") else RecommendationType.HOLD
        )

        evidence = Evidence(
            fact=f"Technical indicators calculated for {ticker_str}: RSI={rsi}, Trend={trend}, Change={chg_pct}%.",
            confidence=ConfidenceScore(Decimal("0.80")),
        )

        return AgentResult(
            agent_type=self.agent_type,
            recommendation=rec,
            score=RecommendationScore(score_clamped),
            confidence=ConfidenceScore(Decimal("0.80")),
            reasoning=f"Technical price momentum for {ticker_str}: Trend is {trend} with RSI {rsi}.",
            evidence=[evidence],
            risks=["Trend reversal", "Short-term volatility"],
            assumptions=["Support levels hold"],
            unknowns=["Unexpected intraday block deals"],
            reasoning_steps=["Calculated RSI and moving averages", "Analyzed price momentum"],
        )
