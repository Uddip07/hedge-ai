"""
RecommendationAggregator Domain Service for the Indian AI Hedge Fund Platform.

Pure domain service converting consensus scores into final Investment Committee recommendations.
Zero infrastructure dependencies.
"""

from decimal import Decimal

from packages.domain.enums.research import RecommendationType
from packages.domain.research.consensus import AgentOpinion, FinalRecommendation
from packages.domain.services.consensus_calculator import ConsensusCalculator
from packages.domain.value_objects.identifiers.ticker import Ticker


class RecommendationAggregator:
    """
    Stateless domain aggregator mapping multi-agent consensus to final actionable trade recommendations.
    """

    @staticmethod
    def aggregate(
        ticker: Ticker,
        opinions: list[AgentOpinion],
    ) -> FinalRecommendation:
        """
        Aggregate multi-agent opinions into a FinalRecommendation payload.
        """
        rec_score, conf_score = ConsensusCalculator.calculate_consensus_score(opinions)
        rec_val = rec_score.value

        # Map score [-1.0, 1.0] to RecommendationType enum
        if rec_val >= Decimal("0.6"):
            final_rec_enum = RecommendationType.STRONG_BUY
        elif rec_val >= Decimal("0.2"):
            final_rec_enum = RecommendationType.BUY
        elif rec_val > Decimal("-0.2"):
            final_rec_enum = RecommendationType.HOLD
        elif rec_val > Decimal("-0.6"):
            final_rec_enum = RecommendationType.SELL
        else:
            final_rec_enum = RecommendationType.STRONG_SELL

        rationale = f"Aggregated {len(opinions)} agent opinions for {ticker.symbol} with consensus score {rec_val:.2f}."

        return FinalRecommendation(
            recommendation=final_rec_enum,
            score=rec_score,
            confidence=conf_score,
            rationale=rationale,
        )
