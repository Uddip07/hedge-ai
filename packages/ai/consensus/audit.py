"""
Audit Recorder and Reasoning Graph Builder for Consensus Intelligence Engine.

Constructs verifiable AuditRecord entries and ReasoningGraph trees for regulatory compliance.
"""

from packages.ai.consensus.models import (
    AuditRecord,
    ReasoningGraph,
    ReasoningGraphEdge,
    ReasoningGraphNode,
)
from packages.ai.models.agent_result import AgentResult
from packages.domain.enums.research import RecommendationType


class AuditRecorder:
    """
    Recorder constructing audit logs and reasoning graph data structures.
    """

    def build_reasoning_graph(
        self,
        results: list[AgentResult],
        winning_rec: RecommendationType,
    ) -> ReasoningGraph:
        """
        Build a structured ReasoningGraph representation from agent results and final recommendation.

        Args:
            results (list[AgentResult]): Agent results list.
            winning_rec (RecommendationType): Final committee recommendation.

        Returns:
            ReasoningGraph: Reasoning graph representation.
        """
        nodes: list[ReasoningGraphNode] = []
        edges: list[ReasoningGraphEdge] = []

        decision_node_id = "node-decision-final"
        nodes.append(
            ReasoningGraphNode(
                id=decision_node_id,
                label=f"Committee Recommendation: {winning_rec.value}",
                node_type="DECISION",
            )
        )

        for idx, res in enumerate(results):
            agent_node_id = f"node-agent-{res.agent_type.value.lower()}"
            nodes.append(
                ReasoningGraphNode(
                    id=agent_node_id,
                    label=f"{res.agent_type.value} Agent ({res.recommendation.value})",
                    node_type="AGENT",
                    metadata={
                        "score": str(res.score.value),
                        "confidence": str(res.confidence.value),
                    },
                )
            )

            # Edge from Agent to Decision
            edges.append(
                ReasoningGraphEdge(
                    source=agent_node_id,
                    target=decision_node_id,
                    relation="VOTED",
                )
            )

            # Add Evidence nodes
            for ev_idx, ev in enumerate(res.evidence):
                ev_node_id = f"node-ev-{idx}-{ev_idx}"
                nodes.append(
                    ReasoningGraphNode(
                        id=ev_node_id,
                        label=ev.fact[:40] + ("..." if len(ev.fact) > 40 else ""),
                        node_type="EVIDENCE",
                    )
                )
                edges.append(
                    ReasoningGraphEdge(
                        source=ev_node_id,
                        target=agent_node_id,
                        relation="SUPPORTS",
                    )
                )

        return ReasoningGraph(nodes=nodes, edges=edges)

    def record_audit(
        self,
        session_id: str,
        results: list[AgentResult],
        applied_weights: dict[str, float],
        conflict_count: int,
        final_recommendation: RecommendationType,
        consensus_score: float,
        confidence_score: float,
        agreement_score: float,
    ) -> AuditRecord:
        """
        Create a cryptographically signed AuditRecord instance.
        """
        return AuditRecord.create(
            session_id=session_id,
            agent_count=len(results),
            weights_applied=applied_weights,
            detected_conflicts_count=conflict_count,
            final_recommendation=final_recommendation.value,
            consensus_score=consensus_score,
            confidence_score=confidence_score,
            agreement_score=agreement_score,
        )
