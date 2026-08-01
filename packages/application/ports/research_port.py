"""
Research Port Interface for the Application Layer.

Defines outbound port contracts for research report storage, thesis retrieval,
and multi-agent consensus scores.
"""

from abc import ABC, abstractmethod

from packages.domain.research.consensus import ConsensusDecision
from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.domain.value_objects.metrics.scores import RecommendationScore


class ResearchPort(ABC):
    """
    Abstract Outbound Port for Investment Research & Committee Consensus Providers.
    """

    @abstractmethod
    def get_research_report(self, report_id: ResearchId) -> ResearchReport | None:
        """
        Retrieve research report by ID.

        Args:
            report_id (ResearchId): Unique research report identifier.

        Returns:
            ResearchReport | None: Research report entity or None if not found.
        """

    @abstractmethod
    def save_research_report(self, report: ResearchReport) -> None:
        """
        Persist or update a research report thesis.

        Args:
            report (ResearchReport): Research report aggregate root to store.
        """

    @abstractmethod
    def get_consensus_decision(self, report_id: ResearchId) -> ConsensusDecision | None:
        """
        Retrieve multi-agent committee consensus decision for a research report.

        Args:
            report_id (ResearchId): Unique research report identifier.

        Returns:
            ConsensusDecision | None: Consensus decision object or None.
        """

    @abstractmethod
    def get_latest_recommendation_score(self, ticker: Ticker) -> RecommendationScore | None:
        """
        Retrieve latest committee recommendation score for a given ticker symbol.

        Args:
            ticker (Ticker): Target asset ticker identifier.

        Returns:
            RecommendationScore | None: Latest recommendation score or None.
        """
