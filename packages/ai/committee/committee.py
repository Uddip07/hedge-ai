"""
Intelligent Investment Committee Facade.

Primary entrypoint exposing high-level methods to execute committee research,
query decision history, calibrate agent performance, and access investment memory.
"""

from typing import Any

from packages.ai.committee.calibration import ConfidenceCalibrator
from packages.ai.committee.exceptions import CommitteeError
from packages.ai.committee.history import DecisionHistoryManager
from packages.ai.committee.models import (
    CommitteeDecision,
    DecisionHistory,
    InvestmentHorizon,
    InvestmentStyle,
    ResearchRequest,
)
from packages.ai.committee.orchestration import CommitteeOrchestrator
from packages.domain.value_objects.identifiers.ticker import Ticker


class IntelligentInvestmentCommittee:
    """
    Top-level Intelligent Investment Committee API facade.
    """

    def __init__(
        self,
        orchestrator: CommitteeOrchestrator | None = None,
        history_manager: DecisionHistoryManager | None = None,
    ) -> None:
        self.orchestrator = orchestrator or CommitteeOrchestrator()
        self.history_manager = history_manager or DecisionHistoryManager()
        self.calibrator = ConfidenceCalibrator(memory=self.orchestrator.memory)

    def evaluate_investment_request(
        self,
        ticker_symbol: str,
        horizon: InvestmentHorizon = InvestmentHorizon.LONG_TERM,
        style: InvestmentStyle = InvestmentStyle.BALANCED,
        user_query: str = "Execute comprehensive investment analysis.",
        session_id: str | None = None,
    ) -> tuple[CommitteeDecision, dict[str, Any]]:
        """
        Execute comprehensive committee analysis for a target ticker.

        Args:
            ticker_symbol (str): Stock ticker symbol.
            horizon (InvestmentHorizon): Target horizon classification.
            style (InvestmentStyle): Target style classification.
            user_query (str): User research prompt.
            session_id (str | None): Optional session ID.

        Returns:
            tuple[CommitteeDecision, dict[str, Any]]: Committee decision aggregate and explanation.
        """
        try:
            ticker = Ticker(ticker_symbol)
            request = ResearchRequest(
                ticker=ticker,
                session_id=session_id or "",
                horizon=horizon,
                style=style,
                user_query=user_query,
            )

            decision, explanation = self.orchestrator.execute_committee_analysis(request)
            self.history_manager.record_decision(
                session_id=request.session_id,
                ticker=ticker,
                decision=decision,
            )

            return decision, explanation
        except Exception as err:
            raise CommitteeError(
                f"Failed to evaluate investment request for '{ticker_symbol}': {err}",
                details={"ticker": ticker_symbol},
            ) from err

    def get_session_history(self, session_id: str) -> list[DecisionHistory]:
        """Query decision history records by session ID."""
        return self.history_manager.get_session_history(session_id)
