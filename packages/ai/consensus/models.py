"""
Models for Consensus Intelligence Engine.

Defines DetectedConflict, ReasoningGraph, AuditRecord, and ConsensusIntelligenceDecision data structures.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from packages.domain.ai.reasoning import Evidence
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


@dataclass(frozen=True)
class DetectedConflict:
    """
    Structured conflict event detected across multi-agent committee opinions.

    Attributes:
        conflict_type (str): Classification (BUY_VS_SELL, BUY_VS_STRONG_SELL, MISSING_EVIDENCE, LOW_CONFIDENCE, CONFLICTING_ASSUMPTIONS).
        severity (str): Impact level (CRITICAL, HIGH, MEDIUM, LOW).
        description (str): Structured textual conflict description.
        involved_agents (list[AgentType]): Agents associated with the conflict.
    """

    conflict_type: str
    severity: str
    description: str
    involved_agents: list[AgentType] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize DetectedConflict to dictionary."""
        return {
            "conflict_type": self.conflict_type,
            "severity": self.severity,
            "description": self.description,
            "involved_agents": [a.value for a in self.involved_agents],
        }


@dataclass(frozen=True)
class ReasoningGraphNode:
    """Node element inside the committee reasoning graph."""

    id: str
    label: str
    node_type: str  # AGENT, EVIDENCE, RISK, DECISION
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ReasoningGraphEdge:
    """Directed edge connecting nodes in the reasoning graph."""

    source: str
    target: str
    relation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
        }


@dataclass(frozen=True)
class ReasoningGraph:
    """Structured graph representation of multi-agent committee reasoning."""

    nodes: list[ReasoningGraphNode] = field(default_factory=list)
    edges: list[ReasoningGraphEdge] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }


@dataclass(frozen=True)
class AuditRecord:
    """
    Cryptographically verifiable audit log record capturing decision telemetry.
    """

    record_id: str
    session_id: str
    timestamp: str
    agent_count: int
    weights_applied: dict[str, float]
    detected_conflicts_count: int
    final_recommendation: str
    consensus_score: float
    confidence_score: float
    agreement_score: float
    hash_signature: str

    @classmethod
    def create(
        cls,
        session_id: str,
        agent_count: int,
        weights_applied: dict[str, float],
        detected_conflicts_count: int,
        final_recommendation: str,
        consensus_score: float,
        confidence_score: float,
        agreement_score: float,
    ) -> "AuditRecord":
        rec_id = str(uuid.uuid4())
        ts = datetime.now(UTC).isoformat()
        raw_str = f"{rec_id}:{session_id}:{ts}:{final_recommendation}:{consensus_score}:{confidence_score}:{agreement_score}"
        sig = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        return AuditRecord(
            record_id=rec_id,
            session_id=session_id,
            timestamp=ts,
            agent_count=agent_count,
            weights_applied=weights_applied,
            detected_conflicts_count=detected_conflicts_count,
            final_recommendation=final_recommendation,
            consensus_score=round(consensus_score, 4),
            confidence_score=round(confidence_score, 4),
            agreement_score=round(agreement_score, 4),
            hash_signature=sig,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "agent_count": self.agent_count,
            "weights_applied": dict(self.weights_applied),
            "detected_conflicts_count": self.detected_conflicts_count,
            "final_recommendation": self.final_recommendation,
            "consensus_score": self.consensus_score,
            "confidence_score": self.confidence_score,
            "agreement_score": self.agreement_score,
            "hash_signature": self.hash_signature,
        }


@dataclass(frozen=True)
class StructuredExplanation:
    """Structured, non-freeform committee decision explanation payload."""

    key_drivers: list[str]
    identified_risks: list[str]
    critical_assumptions: list[str]
    unknowns_and_gaps: list[str]
    policy_compliance_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_drivers": list(self.key_drivers),
            "identified_risks": list(self.identified_risks),
            "critical_assumptions": list(self.critical_assumptions),
            "unknowns_and_gaps": list(self.unknowns_and_gaps),
            "policy_compliance_status": self.policy_compliance_status,
        }


@dataclass(frozen=True)
class ConsensusIntelligenceDecision:
    """
    Comprehensive Output payload generated by the Consensus Intelligence Engine.
    """

    recommendation: RecommendationType
    score: RecommendationScore
    confidence: ConfidenceScore
    agreement_score: float
    evidence: list[Evidence]
    conflicts: list[DetectedConflict]
    explanation: StructuredExplanation
    reasoning_graph: ReasoningGraph
    audit_record: AuditRecord

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendation": self.recommendation.value,
            "score": str(self.score.value),
            "confidence": str(self.confidence.value),
            "agreement_score": round(self.agreement_score, 4),
            "evidence": [e.to_dict() for e in self.evidence],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "explanation": self.explanation.to_dict(),
            "reasoning_graph": self.reasoning_graph.to_dict(),
            "audit_record": self.audit_record.to_dict(),
        }
