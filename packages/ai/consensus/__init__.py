"""
Consensus Intelligence Engine Package.

Exports ConsensusEngine, WeightedConsensusStrategy, ConflictDetector, ConfidenceEngine,
EvidenceAggregator, DecisionExplainer, AuditRecorder, and models.
"""

from packages.ai.consensus.audit import AuditRecorder
from packages.ai.consensus.confidence import ConfidenceEngine, EvidenceAggregator
from packages.ai.consensus.conflicts import ConflictDetector
from packages.ai.consensus.engine import ConsensusEngine
from packages.ai.consensus.explanation import DecisionExplainer
from packages.ai.consensus.models import (
    AuditRecord,
    ConsensusIntelligenceDecision,
    DetectedConflict,
    ReasoningGraph,
    ReasoningGraphEdge,
    ReasoningGraphNode,
    StructuredExplanation,
)
from packages.ai.consensus.weighting import WeightedConsensusStrategy

__all__ = [
    "AuditRecord",
    "AuditRecorder",
    "ConfidenceEngine",
    "ConflictDetector",
    "ConsensusEngine",
    "ConsensusIntelligenceDecision",
    "DecisionExplainer",
    "DetectedConflict",
    "EvidenceAggregator",
    "ReasoningGraph",
    "ReasoningGraphEdge",
    "ReasoningGraphNode",
    "StructuredExplanation",
    "WeightedConsensusStrategy",
]
