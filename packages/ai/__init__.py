"""
Indian AI Hedge Fund - AI Core Framework.

Provides provider-agnostic multi-agent swarm architecture, prompt intelligence framework,
in-memory reasoning/conversation store, consensus intelligence engine, evaluation framework, and orchestrator.
"""

from packages.ai.agents import (
    BaseAgent,
    FundamentalAgent,
    MacroAgent,
    NewsAgent,
    RiskAgent,
    TechnicalAgent,
)
from packages.ai.consensus import (
    AuditRecord,
    AuditRecorder,
    ConfidenceEngine,
    ConflictDetector,
    ConsensusEngine,
    ConsensusIntelligenceDecision,
    DecisionExplainer,
    DetectedConflict,
    EvidenceAggregator,
    ReasoningGraph,
    StructuredExplanation,
    WeightedConsensusStrategy,
)
from packages.ai.evaluation import (
    AgentEvaluator,
    AgentLeaderboardEntry,
    BenchmarkDataset,
    BenchmarkRunner,
    BenchmarkSample,
    CalibrationAnalyzer,
    DatasetManager,
    EvaluationEngine,
    EvaluationMetrics,
    Leaderboard,
    MetricsCalculator,
    ReportGenerator,
)
from packages.ai.memory import ConversationStore
from packages.ai.models import AgentContext, AgentResult
from packages.ai.orchestrator import AgentOrchestrator
from packages.ai.prompts import (
    ContextBuilder,
    PromptComposer,
    PromptRegistry,
    PromptTemplate,
    PromptValidator,
    PromptVersionEntry,
    PromptVersionManager,
    TokenBudgetManager,
)
from packages.ai.reasoning import ReasoningEngine
from packages.ai.tools import BaseTool, ToolRegistry

__version__ = "1.0.0"

__all__ = [
    "AgentContext",
    "AgentEvaluator",
    "AgentLeaderboardEntry",
    "AgentOrchestrator",
    "AgentResult",
    "AuditRecord",
    "AuditRecorder",
    "BaseAgent",
    "BaseTool",
    "BenchmarkDataset",
    "BenchmarkRunner",
    "BenchmarkSample",
    "CalibrationAnalyzer",
    "ConfidenceEngine",
    "ConflictDetector",
    "ConsensusEngine",
    "ConsensusIntelligenceDecision",
    "ContextBuilder",
    "ConversationStore",
    "DatasetManager",
    "DecisionExplainer",
    "DetectedConflict",
    "EvaluationEngine",
    "EvaluationMetrics",
    "EvidenceAggregator",
    "FundamentalAgent",
    "Leaderboard",
    "MacroAgent",
    "MetricsCalculator",
    "NewsAgent",
    "PromptComposer",
    "PromptRegistry",
    "PromptTemplate",
    "PromptValidator",
    "PromptVersionEntry",
    "PromptVersionManager",
    "ReasoningEngine",
    "ReasoningGraph",
    "ReportGenerator",
    "RiskAgent",
    "StructuredExplanation",
    "TechnicalAgent",
    "TokenBudgetManager",
    "ToolRegistry",
    "WeightedConsensusStrategy",
]
