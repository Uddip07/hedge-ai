"""
Weighted Consensus Strategy for Consensus Intelligence Engine.

Computes weighted score aggregations, directional trade recommendations, and committee agreement percentages.
"""

from decimal import Decimal

from packages.ai.models.agent_result import AgentResult
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.metrics.scores import RecommendationScore


class WeightedConsensusStrategy:
    """
    Strategy for computing weighted consensus scores and directional trade signals.
    """

    DEFAULT_WEIGHTS: dict[AgentType, Decimal] = {
        AgentType.FUNDAMENTAL: Decimal("1.2"),
        AgentType.QUANT: Decimal("1.0"),
        AgentType.SENTIMENT: Decimal("0.8"),
        AgentType.RISK: Decimal("1.5"),
        AgentType.MACRO: Decimal("0.9"),
        AgentType.EXECUTION: Decimal("1.0"),
        AgentType.DIRECTOR: Decimal("1.0"),
        AgentType.PORTFOLIO_MANAGER: Decimal("1.5"),
    }

    def compute_weighted_score(
        self,
        results: list[AgentResult],
        weights_override: dict[str, Decimal | float | str] | None = None,
    ) -> tuple[RecommendationScore, RecommendationType, float, dict[str, float]]:
        """
        Compute weighted recommendation score, winning recommendation direction, agreement ratio, and weight map.

        Args:
            results (list[AgentResult]): List of agent research outputs.
            weights_override (dict[str, Any] | None): Optional per-agent weight overrides.

        Returns:
            tuple[RecommendationScore, RecommendationType, float, dict[str, float]]:
                (consensus_score, recommendation, agreement_score, applied_weights)
        """
        if not results:
            return (
                RecommendationScore(Decimal("0.0")),
                RecommendationType.HOLD,
                0.0,
                {},
            )

        applied_weights: dict[str, float] = {}
        total_weighted_score = Decimal("0.0")
        total_weight = Decimal("0.0")

        # Track weight assigned to each recommendation type for agreement calculation
        rec_weight_map: dict[RecommendationType, Decimal] = {
            rec: Decimal("0.0") for rec in RecommendationType
        }

        for res in results:
            agent_type_str = res.agent_type.value
            if weights_override and agent_type_str in weights_override:
                w = Decimal(str(weights_override[agent_type_str]))
            else:
                w = self.DEFAULT_WEIGHTS.get(res.agent_type, Decimal("1.0"))

            applied_weights[agent_type_str] = float(w)
            total_weight += w
            total_weighted_score += res.score.value * w
            rec_weight_map[res.recommendation] += w

        if total_weight > Decimal("0"):
            avg_score_val = total_weighted_score / total_weight
        else:
            avg_score_val = Decimal("0.0")

        rec_score = RecommendationScore(avg_score_val)
        val = rec_score.value

        # Map score range to recommendation direction
        if val >= Decimal("0.75"):
            winning_rec = RecommendationType.STRONG_BUY
        elif val >= Decimal("0.25"):
            winning_rec = RecommendationType.BUY
        elif val >= Decimal("-0.25"):
            winning_rec = RecommendationType.HOLD
        elif val >= Decimal("-0.75"):
            winning_rec = RecommendationType.SELL
        else:
            winning_rec = RecommendationType.STRONG_SELL

        # Calculate agreement ratio: (weight of agents aligned with winning direction) / total_weight
        winning_weight = rec_weight_map.get(winning_rec, Decimal("0.0"))
        agreement_ratio = (
            float(winning_weight / total_weight) if total_weight > Decimal("0") else 0.0
        )

        return rec_score, winning_rec, agreement_ratio, applied_weights
