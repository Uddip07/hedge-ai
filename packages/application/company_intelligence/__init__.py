"""
Company Intelligence Engine Package.

Provides end-to-end Company Intelligence Orchestrator, Pipeline, Workflow, Services,
Models, Exceptions, and ResearchReportBuilder.
"""

from packages.application.company_intelligence.exceptions import (
    CompanyIntelligenceError,
    DocumentRetrievalError,
    PipelineExecutionError,
    ReportGenerationError,
)
from packages.application.company_intelligence.models import (
    AgentOpinionModel,
    AgentOpinionsSection,
    CompanyIntelligenceContext,
    ConsensusDecisionSection,
    CorporateActionsSection,
    ExecutiveSummary,
    ExplainabilitySection,
    FinancialHighlights,
    MacroContextSection,
    MarketSnapshot,
    NewsSection,
    ResearchReport,
    SourceAttribution,
    SupportingEvidence,
    TechnicalAnalysisSection,
)
from packages.application.company_intelligence.orchestrator import (
    CompanyIntelligenceOrchestrator,
)
from packages.application.company_intelligence.pipeline import CompanyIntelligencePipeline
from packages.application.company_intelligence.report_builder import ResearchReportBuilder
from packages.application.company_intelligence.services import (
    CompanyAgentCoordinatorService,
    CompanyDataRetrievalService,
    CompanyDocumentService,
)
from packages.application.company_intelligence.workflow import CompanyIntelligenceWorkflow

__all__ = [
    "CompanyIntelligenceOrchestrator",
    "CompanyIntelligencePipeline",
    "CompanyIntelligenceWorkflow",
    "CompanyIntelligenceContext",
    "MarketSnapshot",
    "FinancialHighlights",
    "TechnicalAnalysisSection",
    "NewsSection",
    "CorporateActionsSection",
    "MacroContextSection",
    "SourceAttribution",
    "SupportingEvidence",
    "AgentOpinionModel",
    "AgentOpinionsSection",
    "ConsensusDecisionSection",
    "ExplainabilitySection",
    "ExecutiveSummary",
    "ResearchReport",
    "ResearchReportBuilder",
    "CompanyDataRetrievalService",
    "CompanyDocumentService",
    "CompanyAgentCoordinatorService",
    "CompanyIntelligenceError",
    "PipelineExecutionError",
    "DocumentRetrievalError",
    "ReportGenerationError",
]
