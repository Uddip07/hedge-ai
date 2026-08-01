"""
Shared Data Models and Transfer Objects for Intelligent Investment Committee.

Defines ResearchRequest, ResearchPlan, ResearchTask, TaskGraph, TaskDependency,
AgentAssignment, EvidenceBundle, Critique, Judgement, CommitteeDecision,
DecisionHistory, MemoryEntry, and CommitteeMetrics.
"""

import json
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Any

from packages.ai.models.agent_result import AgentResult
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


class InvestmentHorizon(StrEnum):
    """Target investment time horizon classification."""

    INTRADAY = "INTRADAY"
    DAILY = "DAILY"
    SWING = "SWING"
    LONG_TERM = "LONG_TERM"


class InvestmentStyle(StrEnum):
    """Target investment management style classification."""

    VALUE = "VALUE"
    GROWTH = "GROWTH"
    QUANTITATIVE = "QUANTITATIVE"
    TECHNICAL = "TECHNICAL"
    BALANCED = "BALANCED"


class TaskStatus(StrEnum):
    """Task graph execution lifecycle status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class ResearchRequest:
    """Input research request received by the Intelligent Investment Committee."""

    ticker: Ticker
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    horizon: InvestmentHorizon = InvestmentHorizon.LONG_TERM
    style: InvestmentStyle = InvestmentStyle.BALANCED
    user_query: str = "Execute comprehensive investment analysis."
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker.full_symbol,
            "session_id": self.session_id,
            "horizon": self.horizon.value,
            "style": self.style.value,
            "user_query": self.user_query,
            "parameters": dict(self.parameters),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ResearchPlan:
    """Optimization plan created by CommitteePlanner."""

    plan_id: str
    session_id: str
    ticker: Ticker
    horizon: InvestmentHorizon
    style: InvestmentStyle
    required_agent_types: list[AgentType]
    required_evidence_types: list[str]
    estimated_duration_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "session_id": self.session_id,
            "ticker": self.ticker.full_symbol,
            "horizon": self.horizon.value,
            "style": self.style.value,
            "required_agent_types": [a.value for a in self.required_agent_types],
            "required_evidence_types": list(self.required_evidence_types),
            "estimated_duration_ms": self.estimated_duration_ms,
        }


@dataclass(frozen=True)
class TaskDependency:
    """Directed dependency link between task graph nodes."""

    parent_task_id: str
    child_task_id: str
    is_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_task_id": self.parent_task_id,
            "child_task_id": self.child_task_id,
            "is_required": self.is_required,
        }


@dataclass
class ResearchTask:
    """Individual execution unit in the committee task graph."""

    task_id: str
    name: str
    agent_type: AgentType | None = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    priority: int = 1
    max_retries: int = 2
    timeout_seconds: float = 30.0
    result: Any | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "agent_type": self.agent_type.value if self.agent_type else None,
            "status": self.status.value,
            "dependencies": list(self.dependencies),
            "priority": self.priority,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "has_result": self.result is not None,
            "error": self.error,
        }


@dataclass
class TaskGraph:
    """Directed Acyclic Graph (DAG) of research tasks."""

    graph_id: str
    tasks: dict[str, ResearchTask] = field(default_factory=dict)
    execution_order: list[str] = field(default_factory=list)

    def add_task(self, task: ResearchTask) -> None:
        self.tasks[task.task_id] = task

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "execution_order": list(self.execution_order),
        }


@dataclass(frozen=True)
class AgentAssignment:
    """Specialist agent committee assignment configuration."""

    agent_type: AgentType
    weight: Decimal
    allocated_budget_tokens: int
    assigned_tasks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_type": self.agent_type.value,
            "weight": str(self.weight),
            "allocated_budget_tokens": self.allocated_budget_tokens,
            "assigned_tasks": list(self.assigned_tasks),
        }


@dataclass(frozen=True)
class EvidenceBundle:
    """Aggregated evidence bundle across market data and document filings."""

    bundle_id: str
    ticker: Ticker
    evidence_items: list[Any]
    total_citations: int
    quality_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "ticker": self.ticker.full_symbol,
            "total_evidence": len(self.evidence_items),
            "total_citations": self.total_citations,
            "quality_score": self.quality_score,
        }


@dataclass(frozen=True)
class Critique:
    """Structured critical evaluation targeting an agent recommendation."""

    critique_id: str
    target_agent: AgentType
    has_contradictions: bool
    weak_assumptions: list[str]
    missing_evidence: list[str]
    overconfidence_flag: bool
    severity: str
    commentary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "critique_id": self.critique_id,
            "target_agent": self.target_agent.value,
            "has_contradictions": self.has_contradictions,
            "weak_assumptions": list(self.weak_assumptions),
            "missing_evidence": list(self.missing_evidence),
            "overconfidence_flag": self.overconfidence_flag,
            "severity": self.severity,
            "commentary": self.commentary,
        }


@dataclass(frozen=True)
class Judgement:
    """Final synthesis evaluation generated by CommitteeJudge."""

    judgement_id: str
    overall_confidence: float
    evidence_strength: float
    recommendation_quality: float
    source_coverage_ratio: float
    verdict_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "judgement_id": self.judgement_id,
            "overall_confidence": self.overall_confidence,
            "evidence_strength": self.evidence_strength,
            "recommendation_quality": self.recommendation_quality,
            "source_coverage_ratio": self.source_coverage_ratio,
            "verdict_summary": self.verdict_summary,
        }


@dataclass(frozen=True)
class CommitteeDecision:
    """Comprehensive decision payload generated by the Intelligent Investment Committee."""

    decision_id: str
    session_id: str
    ticker: Ticker
    winning_recommendation: RecommendationType
    consensus_score: float
    confidence: float
    agreement_ratio: float
    judgement: Judgement
    critiques: list[Critique]
    agent_results: list[AgentResult]
    audit_signature: str
    timestamp: Timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "session_id": self.session_id,
            "ticker": self.ticker.full_symbol,
            "winning_recommendation": self.winning_recommendation.value,
            "consensus_score": self.consensus_score,
            "confidence": self.confidence,
            "agreement_ratio": self.agreement_ratio,
            "judgement": self.judgement.to_dict(),
            "critiques": [c.to_dict() for c in self.critiques],
            "agent_count": len(self.agent_results),
            "audit_signature": self.audit_signature,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


@dataclass(frozen=True)
class DecisionHistory:
    """Historical record of past investment committee decisions."""

    history_id: str
    session_id: str
    ticker: Ticker
    decision: CommitteeDecision
    outcome_evaluated: bool = False
    actual_return_percent: float | None = None
    prediction_accuracy: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "history_id": self.history_id,
            "session_id": self.session_id,
            "ticker": self.ticker.full_symbol,
            "decision": self.decision.to_dict(),
            "outcome_evaluated": self.outcome_evaluated,
            "actual_return_percent": self.actual_return_percent,
            "prediction_accuracy": self.prediction_accuracy,
        }


@dataclass(frozen=True)
class MemoryEntry:
    """Persistent reasoning memory record for investment calibration."""

    entry_id: str
    session_id: str
    ticker: str
    decision_timestamp: str
    recommendation: str
    confidence: float
    evidence_summary: list[str]
    reasoning: str
    actual_outcome: str | None = None
    accuracy_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "session_id": self.session_id,
            "ticker": self.ticker,
            "decision_timestamp": self.decision_timestamp,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "evidence_summary": list(self.evidence_summary),
            "reasoning": self.reasoning,
            "actual_outcome": self.actual_outcome,
            "accuracy_score": self.accuracy_score,
        }


@dataclass(frozen=True)
class CommitteeMetrics:
    """Runtime performance and execution metrics."""

    session_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    execution_time_ms: float
    parallelism_factor: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "execution_time_ms": self.execution_time_ms,
            "parallelism_factor": self.parallelism_factor,
        }


__all__ = [
    "AgentAssignment",
    "AgentResult",
    "CommitteeDecision",
    "CommitteeMetrics",
    "Critique",
    "DecisionHistory",
    "EvidenceBundle",
    "InvestmentHorizon",
    "InvestmentStyle",
    "Judgement",
    "MemoryEntry",
    "ResearchPlan",
    "ResearchRequest",
    "ResearchTask",
    "TaskDependency",
    "TaskGraph",
    "TaskStatus",
]
