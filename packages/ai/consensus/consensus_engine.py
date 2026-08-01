"""
Consensus Engine for AI Core Framework.

Computes weighted committee consensus decisions from multi-agent research outputs.
"""

from decimal import Decimal

from packages.ai.models.agent_result import AgentResult
from packages.domain.research.consensus import (
    AgentOpinion,
    AgentVote,
    ConsensusDecision,
)
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class ConsensusEngine:
    """
    Weighted Consensus Engine converting agent research results into domain ConsensusDecision.
    """

    def compute_consensus(
        self,
        results: list[AgentResult],
        agent_weights: dict[str, Decimal] | None = None,
    ) -> ConsensusDecision:
        """
        Aggregate multi-agent analysis results into a weighted ConsensusDecision.

        Args:
            results (list[AgentResult]): Analysis outputs from research agents.
            agent_weights (dict[str, Decimal] | None): Optional weight overrides per agent_type string.

        Returns:
            ConsensusDecision: Weighted committee consensus decision.
        """
        if not results:
            return ConsensusDecision(
                opinions=[],
                votes=[],
                consensus_score=RecommendationScore(Decimal("0.0")),
                confidence=ConfidenceScore(Decimal("0.5")),
                summary="No agent results provided for consensus calculation.",
            )

        opinions: list[AgentOpinion] = []
        votes: list[AgentVote] = []

        total_weighted_score = Decimal("0.0")
        total_weighted_conf = Decimal("0.0")
        total_weight = Decimal("0.0")

        weights = agent_weights or {}

        for res in results:
            w = weights.get(res.agent_type.value, Decimal("1.0"))
            total_weight += w

            # Weighted metrics
            total_weighted_score += res.score.value * w
            total_weighted_conf += res.confidence.value * w

            # Domain AgentOpinion
            opinion = AgentOpinion(
                agent_type=res.agent_type,
                recommendation=res.recommendation,
                reasoning=res.reasoning,
                confidence=res.confidence,
                supporting_evidence=[e.fact for e in res.evidence],
            )
            opinions.append(opinion)

            # Domain AgentVote
            vote = AgentVote(
                agent_type=res.agent_type,
                recommendation=res.recommendation,
                weight=w,
            )
            votes.append(vote)

        if total_weight > Decimal("0"):
            avg_score = total_weighted_score / total_weight
            avg_conf = total_weighted_conf / total_weight
        else:
            avg_score = Decimal("0.0")
            avg_conf = Decimal("0.5")

        rec_score = RecommendationScore(avg_score)
        conf_score = ConfidenceScore(avg_conf)

        summary = (
            f"Multi-agent committee consensus evaluated across {len(results)} agents "
            f"resulting in weighted score {rec_score.value} and confidence {conf_score.value}."
        )

        return ConsensusDecision(
            opinions=opinions,
            votes=votes,
            consensus_score=rec_score,
            confidence=conf_score,
            summary=summary,
        )
