"""
Confidence Engine and Evidence Aggregator for Consensus Intelligence Engine.

Aggregates evidence items across committee agents and computes penalized composite confidence scores.
"""

from decimal import Decimal

from packages.ai.consensus.models import DetectedConflict
from packages.ai.models.agent_result import AgentResult
from packages.domain.ai.reasoning import Evidence
from packages.domain.value_objects.metrics.scores import ConfidenceScore


class EvidenceAggregator:
    """
    Aggregates, deduplicates, and structures evidence items across agent results.
    """

    def aggregate_evidence(self, results: list[AgentResult]) -> list[Evidence]:
        """
        Collect and deduplicate all evidence items from committee agent results.

        Args:
            results (list[AgentResult]): Agent results list.

        Returns:
            list[Evidence]: Deduplicated evidence list.
        """
        seen_facts: set[str] = set()
        aggregated: list[Evidence] = []

        for res in results:
            for ev in res.evidence:
                fact_clean = ev.fact.strip()
                if fact_clean and fact_clean not in seen_facts:
                    seen_facts.add(fact_clean)
                    aggregated.append(ev)

        return aggregated


class ConfidenceEngine:
    """
    Computes composite confidence scores factoring in weighted agent confidence,
    evidence availability, and conflict penalties.
    """

    def compute_composite_confidence(
        self,
        results: list[AgentResult],
        conflicts: list[DetectedConflict],
        applied_weights: dict[str, float] | None = None,
    ) -> ConfidenceScore:
        """
        Compute penalized composite ConfidenceScore.

        Args:
            results (list[AgentResult]): Committee agent outputs.
            conflicts (list[DetectedConflict]): List of detected conflict events.
            applied_weights (dict[str, float] | None): Applied agent weights dictionary.

        Returns:
            ConfidenceScore: Composite confidence score object.
        """
        if not results:
            return ConfidenceScore(Decimal("0.50"))

        weights = applied_weights or {}
        total_weighted_conf = Decimal("0.0")
        total_weight = Decimal("0.0")

        for res in results:
            w = Decimal(str(weights.get(res.agent_type.value, 1.0)))
            total_weight += w
            total_weighted_conf += res.confidence.value * w

        if total_weight > Decimal("0"):
            base_conf = total_weighted_conf / total_weight
        else:
            base_conf = Decimal("0.50")

        # Apply conflict penalties
        penalty = Decimal("0.0")
        for conflict in conflicts:
            if conflict.severity == "CRITICAL":
                penalty += Decimal("0.25")
            elif conflict.severity == "HIGH":
                penalty += Decimal("0.15")
            elif conflict.severity == "MEDIUM":
                penalty += Decimal("0.05")

        final_conf_val = max(Decimal("0.0"), min(Decimal("1.0"), base_conf - penalty))
        return ConfidenceScore(final_conf_val)
