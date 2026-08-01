"""
SQL Research Adapter — Production ResearchPort Implementation.

Implements the application ResearchPort by delegating to SQLResearchRepository
for persistent storage. Returns None from get_latest_recommendation_score()
when no research exists, triggering the AI committee to generate a real score.
"""

from packages.application.ports.research_port import ResearchPort
from packages.domain.research.consensus import ConsensusDecision
from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.domain.value_objects.metrics.scores import RecommendationScore
from packages.infrastructure.repositories.research_repository import SQLResearchRepository


class SQLResearchAdapter(ResearchPort):
    """
    Production Research Port Adapter backed by SQLResearchRepository.

    This is the production implementation of ResearchPort. It reads and writes
    ResearchReport aggregates to the SQL store. Unlike MockResearchAdapter,
    get_latest_recommendation_score() returns None when no score is stored —
    this signals to the use case that a real AI committee evaluation is required.
    """

    def __init__(self, repository: SQLResearchRepository | None = None) -> None:
        self._repo = repository or SQLResearchRepository()

    def get_research_report(self, report_id: ResearchId) -> ResearchReport | None:
        """Retrieve persisted research report by ID."""
        return self._repo.get_by_id(report_id)

    def save_research_report(self, report: ResearchReport) -> None:
        """Persist research report to SQL store."""
        self._repo.save(report)

    def get_consensus_decision(self, report_id: ResearchId) -> ConsensusDecision | None:
        """Return consensus decision from the stored research report if it exists."""
        report = self._repo.get_by_id(report_id)
        if report is not None and report.consensus is not None:
            return report.consensus
        return None

    def get_latest_recommendation_score(self, ticker: Ticker) -> RecommendationScore | None:
        """
        Return the latest recommendation score for a ticker from the SQL store.

        Returns None if no research report exists for this ticker, which causes
        the use case to apply the neutral baseline (HOLD) and schedule a real
        AI committee evaluation.
        """
        report = self._repo.get_by_ticker(ticker)
        if report is None or report.consensus is None:
            return None
        return report.consensus.consensus_score
