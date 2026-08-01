"""
Committee Explainer Implementation.

Generates structured reasoning explaining Planning Process, Task Graph execution, Executed Agents,
Evidence Used, Critic Findings, Judge Findings, Consensus Summary, Unknowns, Assumptions, and Confidence.
Never returns unexplained recommendations.
"""

from typing import Any

from packages.ai.committee.models import (
    Critique,
    Judgement,
    ResearchPlan,
    TaskGraph,
)
from packages.ai.models.agent_result import AgentResult


class CommitteeExplainer:
    """
    Explainer assembling comprehensive institutional reasoning payloads.
    """

    def generate_explanation(
        self,
        plan: ResearchPlan,
        graph: TaskGraph,
        agent_results: list[AgentResult],
        critiques: list[Critique],
        judgement: Judgement,
        consensus_decision: Any,
    ) -> dict[str, Any]:
        """
        Generate complete, structured reasoning payload for CommitteeDecision.

        Returns:
            dict[str, Any]: Formatted explanation dictionary.
        """
        planning_summary = (
            f"Plan '{plan.plan_id}': Target Horizon={plan.horizon.value}, Style={plan.style.value}. "
            f"Selected {len(plan.required_agent_types)} necessary agents minimizing redundant execution."
        )

        graph_summary = (
            f"Task Graph '{graph.graph_id}': Total Tasks={len(graph.tasks)}. "
            f"Execution Order: {' -> '.join(graph.execution_order)}."
        )

        agent_summaries = [
            {
                "agent": res.agent_type.value,
                "recommendation": res.recommendation.value,
                "score": float(res.score.value),
                "confidence": float(res.confidence.value),
                "reasoning": res.reasoning,
                "evidence_count": len(res.evidence),
            }
            for res in agent_results
        ]

        critic_findings = [c.to_dict() for c in critiques]
        judge_finding = judgement.to_dict()

        rec_val = (
            consensus_decision.recommendation.value
            if hasattr(consensus_decision, "recommendation")
            else "HOLD"
        )
        score_val = (
            float(consensus_decision.score.value) if hasattr(consensus_decision, "score") else 0.0
        )
        conf_val = (
            float(consensus_decision.confidence.value)
            if hasattr(consensus_decision, "confidence")
            else 0.50
        )

        consensus_summary = f"Consensus Engine Recommendation: {rec_val} (Score: {score_val}, Confidence: {conf_val})."

        all_assumptions = [a for res in agent_results for a in res.assumptions]
        all_unknowns = [u for res in agent_results for u in res.unknowns]

        return {
            "planning_process": planning_summary,
            "task_graph_execution": graph_summary,
            "executed_agents": agent_summaries,
            "critic_findings": critic_findings,
            "judge_findings": judge_finding,
            "consensus_summary": consensus_summary,
            "assumptions": list(set(all_assumptions)),
            "unknowns": list(set(all_unknowns)),
            "final_confidence": judgement.overall_confidence,
        }
