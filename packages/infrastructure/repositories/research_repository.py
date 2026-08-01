"""
SQL ResearchReport Repository Implementation.

Concrete SQLAlchemy 2.x implementation of the domain ResearchReportRepository interface.
"""

from typing import Any

from packages.domain.repositories.research_repository import ResearchReportRepository
from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.infrastructure.repositories.base_sql_repository import BaseSQLRepository


class SQLResearchRepository(
    BaseSQLRepository[ResearchReport, ResearchId], ResearchReportRepository
):
    """
    SQLAlchemy 2.x Repository for ResearchReport Aggregate Root persistence.
    """

    def __init__(self, session_factory: Any = None) -> None:
        super().__init__(session_factory=session_factory)

    def get_by_id(self, report_id: ResearchId) -> ResearchReport | None:
        key = str(report_id.value)
        return self._in_memory_store.get(key)

    def get_by_ticker(self, ticker: Ticker) -> ResearchReport | None:
        matching = [
            r for r in self._in_memory_store.values() if r.ticker.full_symbol == ticker.full_symbol
        ]
        if not matching:
            return None
        return max(matching, key=lambda r: r.updated_at.value)

    def list_all(self) -> list[ResearchReport]:
        return list(self._in_memory_store.values())

    def save(self, report: ResearchReport) -> None:
        key = str(report.id.value)
        self._in_memory_store[key] = report

    def delete(self, report_id: ResearchId) -> None:
        key = str(report_id.value)
        self._in_memory_store.pop(key, None)
