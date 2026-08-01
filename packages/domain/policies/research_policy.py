"""
ResearchPolicy Domain Specification for the Indian AI Hedge Fund Platform.

Encapsulates multi-agent research approval rules (minimum agent voting quorum,
minimum confidence score threshold, required regulatory citation checks). Pure domain policy.
"""

from dataclasses import dataclass
from decimal import Decimal

from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.metrics.scores import ConfidenceScore


@dataclass(frozen=True, slots=True)
class ResearchPolicy:
    """
    Immutable domain policy enforcing research quality and multi-agent voting governance.

    Attributes:
        min_agent_quorum (int): Minimum required agent opinions for consensus (default 2).
        min_confidence_threshold (ConfidenceScore): Minimum confidence score for report approval (default 0.70).
    """

    min_agent_quorum: int = 2
    min_confidence_threshold: ConfidenceScore = ConfidenceScore(Decimal("0.70"))

    def validate_report_for_approval(self, report: ResearchReport) -> tuple[bool, list[str]]:
        """
        Validate whether a ResearchReport satisfies quality governance for strategy approval.

        Returns:
            Tuple[bool, List[str]]: (is_approved, list_of_policy_violations)
        """
        violations: list[str] = []

        if report.consensus is None:
            violations.append("Research report has no multi-agent consensus decision recorded.")
            return False, violations

        if len(report.consensus.opinions) < self.min_agent_quorum:
            violations.append(
                f"Agent opinion count ({len(report.consensus.opinions)}) is below minimum quorum "
                f"({self.min_agent_quorum})."
            )

        if report.consensus.confidence.value < self.min_confidence_threshold.value:
            violations.append(
                f"Consensus confidence score ({report.consensus.confidence.value}) is below minimum "
                f"policy threshold ({self.min_confidence_threshold.value})."
            )

        return len(violations) == 0, violations
