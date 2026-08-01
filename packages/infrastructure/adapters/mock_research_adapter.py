"""
Mock Research Adapter implementing Application ResearchPort.
"""

from decimal import Decimal

from packages.application.ports.research_port import ResearchPort
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.research.consensus import AgentOpinion, ConsensusDecision
from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class MockResearchAdapter(ResearchPort):
    """
    In-memory Mock Adapter implementing ResearchPort.
    """

    def __init__(self) -> None:
        self.reports: dict[str, ResearchReport] = {}
        self.scores: dict[str, RecommendationScore] = {}

    def get_research_report(self, report_id: ResearchId) -> ResearchReport | None:
        return self.reports.get(str(report_id.value))

    def save_research_report(self, report: ResearchReport) -> None:
        self.reports[str(report.id.value)] = report

    def get_consensus_decision(self, report_id: ResearchId) -> ConsensusDecision | None:
        report = self.get_research_report(report_id)
        if report and report.consensus:
            return report.consensus

        opinion = AgentOpinion(
            agent_type=AgentType.QUANT,
            recommendation=RecommendationType.BUY,
            reasoning="Mock analysis reasoning",
            confidence=ConfidenceScore(Decimal("0.85")),
        )
        return ConsensusDecision(
            opinions=[opinion],
            votes=[],
            consensus_score=RecommendationScore(Decimal("0.80")),
            confidence=ConfidenceScore(Decimal("0.85")),
            summary="Mock consensus decision summary",
        )

    def get_latest_recommendation_score(self, ticker: Ticker) -> RecommendationScore | None:
        return self.scores.get(ticker.full_symbol, RecommendationScore(Decimal("0.75")))
