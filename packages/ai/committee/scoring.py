"""
Scoring and Evaluation Calculations for Intelligent Investment Committee.

Provides evidence quality scoring, agreement calculations, and composite confidence adjustments.
"""

from typing import Any

from packages.ai.models.agent_result import AgentResult


class CommitteeScorer:
    """
    Utility methods computing evidence quality, agreement ratios, and composite scores.
    """

    @staticmethod
    def calculate_evidence_quality(evidence_items: list[Any]) -> float:
        """Calculate evidence quality score based on citation completeness."""
        if not evidence_items:
            return 0.0

        scores: list[float] = []
        for ev in evidence_items:
            citations = getattr(ev, "citations", [])
            has_citation = len(citations) > 0
            base_score = 0.70 if has_citation else 0.40
            scores.append(base_score)

        return round(sum(scores) / len(scores), 2)

    @staticmethod
    def calculate_agent_agreement(results: list[AgentResult]) -> float:
        """Calculate recommendation agreement ratio across committee agents."""
        if not results:
            return 0.0

        recs = [r.recommendation.value for r in results]
        most_common_count = max(recs.count(r) for r in set(recs))
        return round(most_common_count / len(results), 2)

    @staticmethod
    def calculate_composite_confidence(results: list[AgentResult], conflict_count: int) -> float:
        """Calculate composite confidence penalized by conflict count."""
        if not results:
            return 0.50

        avg_conf = sum(float(r.confidence.value) for r in results) / len(results)
        penalty = min(conflict_count * 0.05, 0.30)
        return max(0.0, round(avg_conf - penalty, 2))
