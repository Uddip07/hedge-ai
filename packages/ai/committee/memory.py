"""
Investment Memory Implementation.

Persistent reasoning memory storing investment recommendations, supporting evidence,
confidence scores, reasoning traces, decision timestamps, actual outcomes, and prediction accuracy.
Does NOT implement chat memory.
"""

from packages.ai.committee.exceptions import MemoryError
from packages.ai.committee.models import MemoryEntry


class InvestmentMemory:
    """
    Persistent reasoning memory engine for investment decisions and calibration hooks.
    """

    def __init__(self) -> None:
        self._entries: dict[str, MemoryEntry] = {}

    def store_entry(self, entry: MemoryEntry) -> None:
        """Store a new MemoryEntry record."""
        try:
            self._entries[entry.entry_id] = entry
        except Exception as err:
            raise MemoryError(f"Failed to store memory entry: {err}") from err

    def get_entry(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve MemoryEntry by ID."""
        return self._entries.get(entry_id)

    def search_by_ticker(self, ticker: str) -> list[MemoryEntry]:
        """Search memory entries by stock ticker symbol."""
        return [e for e in self._entries.values() if e.ticker == ticker]

    def update_outcome(
        self, entry_id: str, actual_outcome: str, accuracy_score: float
    ) -> MemoryEntry:
        """Update historical outcome and prediction accuracy score for calibration."""
        entry = self._entries.get(entry_id)
        if not entry:
            raise MemoryError(f"Memory entry '{entry_id}' not found.")

        updated = MemoryEntry(
            entry_id=entry.entry_id,
            session_id=entry.session_id,
            ticker=entry.ticker,
            decision_timestamp=entry.decision_timestamp,
            recommendation=entry.recommendation,
            confidence=entry.confidence,
            evidence_summary=entry.evidence_summary,
            reasoning=entry.reasoning,
            actual_outcome=actual_outcome,
            accuracy_score=round(accuracy_score, 2),
        )
        self._entries[entry_id] = updated
        return updated

    def get_all_entries(self) -> list[MemoryEntry]:
        """Return all persistent memory entries."""
        return list(self._entries.values())
