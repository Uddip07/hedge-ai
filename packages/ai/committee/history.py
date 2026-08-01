"""
Decision History Manager.

Manages persistent DecisionHistory logs for institutional audit and accuracy tracking.
"""

from packages.ai.committee.models import CommitteeDecision, DecisionHistory
from packages.domain.value_objects.identifiers.ticker import Ticker


class DecisionHistoryManager:
    """
    Manager capturing and querying DecisionHistory logs across analysis sessions.
    """

    def __init__(self) -> None:
        self._history_records: dict[str, DecisionHistory] = {}

    def record_decision(
        self, session_id: str, ticker: Ticker, decision: CommitteeDecision
    ) -> DecisionHistory:
        """Record a new CommitteeDecision into DecisionHistory log."""
        hid = f"hist-{decision.decision_id}"
        record = DecisionHistory(
            history_id=hid,
            session_id=session_id,
            ticker=ticker,
            decision=decision,
            outcome_evaluated=False,
        )
        self._history_records[hid] = record
        return record

    def get_history(self, history_id: str) -> DecisionHistory | None:
        """Retrieve DecisionHistory by ID."""
        return self._history_records.get(history_id)

    def get_session_history(self, session_id: str) -> list[DecisionHistory]:
        """Query decision history by session ID."""
        return [r for r in self._history_records.values() if r.session_id == session_id]

    def get_ticker_history(self, ticker_symbol: str) -> list[DecisionHistory]:
        """Query decision history by ticker symbol."""
        return [r for r in self._history_records.values() if r.ticker.full_symbol == ticker_symbol]
