"""
Intelligent Investment Committee Package.

Provides Planner, Task Graph, Scheduler, Critic, Judge, Committee,
Investment Memory, Decision History, Confidence Calibration, and Explainer.
"""

from packages.ai.committee.calibration import ConfidenceCalibrator
from packages.ai.committee.committee import IntelligentInvestmentCommittee
from packages.ai.committee.critic import CommitteeCritic
from packages.ai.committee.exceptions import (
    CommitteeError,
    CritiqueError,
    JudgementError,
    MemoryError,
    PlanningError,
    SchedulerError,
    TaskGraphError,
)
from packages.ai.committee.explanation import CommitteeExplainer
from packages.ai.committee.history import DecisionHistoryManager
from packages.ai.committee.judge import CommitteeJudge
from packages.ai.committee.memory import InvestmentMemory
from packages.ai.committee.models import (
    AgentAssignment,
    AgentResult,
    CommitteeDecision,
    CommitteeMetrics,
    Critique,
    DecisionHistory,
    EvidenceBundle,
    InvestmentHorizon,
    InvestmentStyle,
    Judgement,
    MemoryEntry,
    ResearchPlan,
    ResearchRequest,
    ResearchTask,
    TaskDependency,
    TaskGraph,
    TaskStatus,
)
from packages.ai.committee.orchestration import CommitteeOrchestrator
from packages.ai.committee.planner import CommitteePlanner
from packages.ai.committee.policies import AgentWeightPolicy, ExecutionPolicy
from packages.ai.committee.scheduler import CommitteeScheduler
from packages.ai.committee.scoring import CommitteeScorer
from packages.ai.committee.task_graph import TaskGraphEngine

__version__ = "1.0.0"

__all__ = [
    "AgentAssignment",
    "AgentResult",
    "AgentWeightPolicy",
    "CommitteeCritic",
    "CommitteeDecision",
    "CommitteeError",
    "CommitteeExplainer",
    "CommitteeJudge",
    "CommitteeMetrics",
    "CommitteeOrchestrator",
    "CommitteePlanner",
    "CommitteeScheduler",
    "CommitteeScorer",
    "ConfidenceCalibrator",
    "Critique",
    "CritiqueError",
    "DecisionHistory",
    "DecisionHistoryManager",
    "EvidenceBundle",
    "ExecutionPolicy",
    "IntelligentInvestmentCommittee",
    "InvestmentHorizon",
    "InvestmentMemory",
    "InvestmentStyle",
    "Judgement",
    "JudgementError",
    "MemoryEntry",
    "MemoryError",
    "PlanningError",
    "ResearchPlan",
    "ResearchRequest",
    "ResearchTask",
    "SchedulerError",
    "TaskDependency",
    "TaskGraph",
    "TaskGraphEngine",
    "TaskGraphError",
    "TaskStatus",
]
