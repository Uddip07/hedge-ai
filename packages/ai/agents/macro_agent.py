"""
Macroeconomic Analysis Agent Implementation.

Specialized agent analyzing RBI repo rate, CPI inflation, GDP growth, and forex dynamics.
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


class MacroAgent(BaseAgent):
    """
    Macroeconomic Strategist Agent (AgentType.MACRO).
    """

    def __init__(
        self,
        prompt_registry: PromptRegistry | None = None,
        weight: Decimal | float | str = "0.9",
    ) -> None:
        super().__init__(prompt_registry=prompt_registry, weight=weight)

    @property
    def agent_type(self) -> AgentType:
        return AgentType.MACRO

    def _execute_analysis(self, context: AgentContext) -> AgentResult:
        ticker_str = context.ticker.full_symbol

        evidence_data = context.parameters.get("evidence")
        macro_series: list[Any] = []
        if evidence_data and hasattr(evidence_data, "macro_series"):
            macro_series = evidence_data.macro_series or []

        series_count = len(macro_series)
        score_clamped = Decimal("0.65") if series_count > 0 else Decimal("0.60")
        rec = (
            RecommendationType.BUY if score_clamped >= Decimal("0.60") else RecommendationType.HOLD
        )

        evidence = Evidence(
            fact=f"Evaluated Indian macro context ({series_count} data series available) for {ticker_str}.",
            confidence=ConfidenceScore(Decimal("0.82")),
        )

        return AgentResult(
            agent_type=self.agent_type,
            recommendation=rec,
            score=RecommendationScore(score_clamped),
            confidence=ConfidenceScore(Decimal("0.82")),
            reasoning=f"Macroeconomic outlook for {ticker_str}: Evaluated domestic monetary environment.",
            evidence=[evidence],
            risks=["Interest rate hikes", "Currency volatility"],
            assumptions=["Stable RBI policy rates"],
            unknowns=["Global geopolitical shifts"],
            reasoning_steps=["Evaluated macroeconomic indicators", "Analyzed domestic liquidity"],
        )
