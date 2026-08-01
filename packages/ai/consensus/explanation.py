"""
Decision Explainer for Consensus Intelligence Engine.

Generates structured explanations (key drivers, risk factors, policy compliance, committee alignment summary).
Never generates free-form unformatted paragraphs.
"""

from packages.ai.consensus.models import DetectedConflict, StructuredExplanation
from packages.ai.models.agent_result import AgentResult
from packages.domain.enums.research import RecommendationType


class DecisionExplainer:
    """
    Explainer generating structured decision rationale.
    """

    def explain(
        self,
        recommendation: RecommendationType,
        results: list[AgentResult],
        conflicts: list[DetectedConflict],
    ) -> StructuredExplanation:
        """
        Generate a StructuredExplanation object from committee results and conflicts.

        Args:
            recommendation (RecommendationType): Winning trade recommendation direction.
            results (list[AgentResult]): Agent results list.
            conflicts (list[DetectedConflict]): Detected conflicts list.

        Returns:
            StructuredExplanation: Structured explanation payload.
        """
        key_drivers: list[str] = []
        identified_risks: list[str] = []
        critical_assumptions: list[str] = []
        unknowns_and_gaps: list[str] = []

        for res in results:
            # Extract key reasoning driver
            if res.reasoning and res.reasoning.strip():
                key_drivers.append(f"[{res.agent_type.value}]: {res.reasoning}")

            # Collect risks, assumptions, unknowns
            for r in res.risks:
                if r not in identified_risks:
                    identified_risks.append(r)
            for a in res.assumptions:
                if a not in critical_assumptions:
                    critical_assumptions.append(a)
            for u in res.unknowns:
                if u not in unknowns_and_gaps:
                    unknowns_and_gaps.append(u)

        # Fallback defaults if list items empty
        if not key_drivers:
            key_drivers.append(f"Committee consensus vote favoring {recommendation.value}.")
        if not identified_risks:
            identified_risks.append("Market volatility and systemic sector drawdown risks.")
        if not critical_assumptions:
            critical_assumptions.append(
                "Continued domestic earnings trajectory and stable interest rate environment."
            )
        if not unknowns_and_gaps:
            unknowns_and_gaps.append("Unscheduled geopolitical events or regulatory policy shifts.")

        # Determine compliance status
        critical_conflicts = [c for c in conflicts if c.severity == "CRITICAL"]
        if critical_conflicts:
            compliance_status = f"FLAGGED_CRITICAL_CONFLICT: {critical_conflicts[0].description}"
        elif conflicts:
            compliance_status = (
                f"PASSED_WITH_WARNINGS ({len(conflicts)} non-critical conflict events)"
            )
        else:
            compliance_status = "FULLY_COMPLIANT_UNANIMOUS_OR_ALIGNED"

        return StructuredExplanation(
            key_drivers=key_drivers,
            identified_risks=identified_risks,
            critical_assumptions=critical_assumptions,
            unknowns_and_gaps=unknowns_and_gaps,
            policy_compliance_status=compliance_status,
        )
