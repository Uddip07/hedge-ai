"""
ConsensusCalculator Domain Service for the Indian AI Hedge Fund Platform.

Pure domain service aggregating multi-agent opinions into consensus scores and voting metrics.
Zero infrastructure dependencies.
"""

from decimal import Decimal

from packages.domain.research.consensus import AgentOpinion
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class ConsensusCalculator:
    """
    Stateless domain calculator for AI committee research consensus derivation.
    """

    @staticmethod
    def calculate_consensus_score(
        opinions: list[AgentOpinion],
    ) -> tuple[RecommendationScore, ConfidenceScore]:
        """
        Calculate weighted average recommendation score [-1.0, 1.0] and average confidence score [0, 1].

        Returns:
            Tuple[RecommendationScore, ConfidenceScore]: (consensus_recommendation_score, consensus_confidence)
        """
        if not opinions:
            return RecommendationScore(Decimal("0.0")), ConfidenceScore(Decimal("0.0"))

        total_weight = Decimal("0.0")
        weighted_rec_score = Decimal("0.0")
        total_confidence = Decimal("0.0")

        for op in opinions:
            conf_val = op.confidence.value
            # RecommendationType.score() maps +2 down to -2; normalize to [-1.0, 1.0]
            norm_rec = Decimal(str(op.recommendation.score())) / Decimal("2.0")

            weighted_rec_score += norm_rec * conf_val
            total_weight += conf_val
            total_confidence += conf_val

        count_dec = Decimal(str(len(opinions)))
        avg_confidence = total_confidence / count_dec

        if total_weight > Decimal("0"):
            final_rec_val = weighted_rec_score / total_weight
        else:
            final_rec_val = Decimal("0.0")

        return RecommendationScore(final_rec_val), ConfidenceScore(avg_confidence)
