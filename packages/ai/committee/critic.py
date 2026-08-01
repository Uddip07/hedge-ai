"""
Committee Critic Implementation.

Challenges specialist agent recommendations by detecting contradictions across agent votes,
unsupported claims, weak assumptions, missing evidence citations, and overconfidence flags.
Never generates recommendations.
"""

import uuid

from packages.ai.committee.exceptions import CritiqueError
from packages.ai.committee.models import Critique
from packages.ai.models.agent_result import AgentResult


class CommitteeCritic:
    """
    Adversarial Critic evaluating committee agent outputs for contradictions and weaknesses.
    """

    def generate_critiques(self, agent_results: list[AgentResult]) -> list[Critique]:
        """
        Evaluate list of AgentResult payloads and generate structured Critique instances.

        Args:
            agent_results (list[AgentResult]): Specialist agent analysis results.

        Returns:
            list[Critique]: List of critical evaluations.
        """
        try:
            critiques: list[Critique] = []
            if not agent_results:
                return critiques

            recs = {res.agent_type: res.recommendation for res in agent_results}

            for res in agent_results:
                cid = f"critique-{uuid.uuid4().hex[:8]}"
                contradictions = False
                weak_assumptions: list[str] = list(res.assumptions)
                missing_evidence: list[str] = []
                overconfidence = False

                # 1. Detect Contradictions (e.g. Fundamental BUY vs Technical/Risk SELL)
                for other_agent, other_rec in recs.items():
                    if other_agent != res.agent_type:
                        if ("BUY" in res.recommendation.value and "SELL" in other_rec.value) or (
                            "SELL" in res.recommendation.value and "BUY" in other_rec.value
                        ):
                            contradictions = True

                # 2. Detect Missing Evidence
                if not res.evidence:
                    missing_evidence.append(
                        f"No supporting evidence citations provided for {res.agent_type.value}."
                    )

                # 3. Detect Overconfidence (Confidence > 0.90 but contains risks/unknowns)
                if float(res.confidence.value) >= 0.90 and (res.risks or res.unknowns):
                    overconfidence = True

                severity = "HIGH" if contradictions or missing_evidence else "LOW"
                commentary = (
                    f"Critic review for {res.agent_type.value}: Contradictions={contradictions}, "
                    f"Overconfidence={overconfidence}, EvidenceCount={len(res.evidence)}."
                )

                critiques.append(
                    Critique(
                        critique_id=cid,
                        target_agent=res.agent_type,
                        has_contradictions=contradictions,
                        weak_assumptions=weak_assumptions,
                        missing_evidence=missing_evidence,
                        overconfidence_flag=overconfidence,
                        severity=severity,
                        commentary=commentary,
                    )
                )

            return critiques
        except Exception as err:
            raise CritiqueError(
                f"Committee Critic evaluation failed: {err}",
            ) from err
