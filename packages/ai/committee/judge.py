"""
Committee Judge Implementation.

Evaluates evidence quality, agent reliability, conflicts, confidence penalties, and source coverage
to issue an authoritative Judgement verdict payload.
"""

import uuid

from packages.ai.committee.exceptions import JudgementError
from packages.ai.committee.models import Critique, Judgement
from packages.ai.committee.scoring import CommitteeScorer
from packages.ai.models.agent_result import AgentResult


class CommitteeJudge:
    """
    Judge evaluating committee evidence strength and recommendation quality.
    """

    def evaluate_judgement(
        self, agent_results: list[AgentResult], critiques: list[Critique]
    ) -> Judgement:
        """
        Synthesize agent results and critiques into a unified Judgement.

        Args:
            agent_results (list[AgentResult]): Specialist agent results.
            critiques (list[Critique]): Critic evaluations.

        Returns:
            Judgement: Synthesized committee judgement.
        """
        try:
            jid = f"judgement-{uuid.uuid4().hex[:8]}"

            if not agent_results:
                return Judgement(
                    judgement_id=jid,
                    overall_confidence=0.50,
                    evidence_strength=0.0,
                    recommendation_quality=0.50,
                    source_coverage_ratio=0.0,
                    verdict_summary="No agent results available for judgement evaluation.",
                )

            # 1. Calculate Evidence Strength
            all_evidence = [ev for res in agent_results for ev in res.evidence]
            evidence_strength = CommitteeScorer.calculate_evidence_quality(all_evidence)

            # 2. Calculate Source Coverage Ratio
            agents_with_evidence = sum(1 for res in agent_results if len(res.evidence) > 0)
            source_coverage_ratio = round(agents_with_evidence / len(agent_results), 2)

            # 3. Calculate Conflicts & Overconfidence Penalties
            conflict_count = sum(1 for c in critiques if c.has_contradictions)
            overconfidence_count = sum(1 for c in critiques if c.overconfidence_flag)

            base_confidence = float(
                sum(float(res.confidence.value) for res in agent_results) / len(agent_results)
            )
            penalties = (conflict_count * 0.10) + (overconfidence_count * 0.05)
            overall_confidence = max(0.20, round(base_confidence - penalties, 2))

            # 4. Compute Recommendation Quality
            agreement_ratio = CommitteeScorer.calculate_agent_agreement(agent_results)
            recommendation_quality = round((evidence_strength + agreement_ratio) / 2.0, 2)

            verdict_summary = (
                f"Committee Judgement: Confidence={overall_confidence}, EvidenceStrength={evidence_strength}, "
                f"Quality={recommendation_quality}, SourceCoverage={source_coverage_ratio}."
            )

            return Judgement(
                judgement_id=jid,
                overall_confidence=overall_confidence,
                evidence_strength=evidence_strength,
                recommendation_quality=recommendation_quality,
                source_coverage_ratio=source_coverage_ratio,
                verdict_summary=verdict_summary,
            )
        except Exception as err:
            raise JudgementError(
                f"Committee Judge synthesis failed: {err}",
            ) from err
