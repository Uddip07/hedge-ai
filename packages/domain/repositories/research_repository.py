"""
ResearchReport Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for ResearchReport Aggregate Root persistence.
Pure domain interface with zero infrastructure dependencies.
"""

from abc import ABC, abstractmethod

from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId


class ResearchReportRepository(ABC):
    """
    Abstract Repository Interface for ResearchReport Aggregate Root persistence.
    """

    @abstractmethod
    def get_by_id(self, report_id: ResearchId) -> ResearchReport | None:
        """Fetch ResearchReport Aggregate Root by unique ResearchId."""
        pass

    @abstractmethod
    def get_by_ticker(self, ticker: Ticker) -> ResearchReport | None:
        """Fetch latest ResearchReport for a given asset Ticker."""
        pass

    @abstractmethod
    def list_all(self) -> list[ResearchReport]:
        """List all research reports."""
        pass

    @abstractmethod
    def save(self, report: ResearchReport) -> None:
        """Persist or update a ResearchReport Aggregate Root."""
        pass

    @abstractmethod
    def delete(self, report_id: ResearchId) -> None:
        """Delete a ResearchReport Aggregate Root by ID."""
        pass
