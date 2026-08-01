"""
Paper Trading Isolation Module.

Enforces clean separation between Paper Trading positions/orders and Live Zerodha accounts.
Prevents cross-contamination of positions, state, or execution routing.
"""

import logging
from dataclasses import dataclass
from typing import Any

from packages.domain.enums.portfolio import PortfolioType
from packages.domain.portfolio.holding import Holding
from packages.domain.portfolio.position import Position
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId
from packages.infrastructure.brokers.zerodha import ZerodhaPortfolioManager

logger = logging.getLogger("ihf_ai.application.execution.paper_trading_isolation")


class PaperTradingIsolationError(Exception):
    """Raised when paper trading isolation rules are violated."""


@dataclass
class PortfolioContext:
    """Isolated execution context container."""

    portfolio_id: PortfolioId
    portfolio_type: PortfolioType
    is_live_broker: bool

    def validate_isolation(self, target_is_live: bool) -> None:
        """Assert that target broker type matches portfolio context."""
        if self.is_live_broker != target_is_live:
            raise PaperTradingIsolationError(
                f"Isolation breach! Attempted to execute {'LIVE' if target_is_live else 'PAPER'} trade "
                f"on {'LIVE' if self.is_live_broker else 'PAPER'} portfolio context {self.portfolio_id}."
            )


class PaperTradingManager:
    """
    Manages paper trading portfolios and ensures zero overlap with live Zerodha accounts.
    """

    def __init__(self) -> None:
        self._paper_holdings: dict[str, list[Holding]] = {}
        self._paper_positions: dict[str, list[Position]] = {}

    def create_paper_portfolio_context(self, name: str = "default_paper") -> PortfolioContext:
        """Create an isolated paper portfolio context."""
        pid = PortfolioId.generate()
        return PortfolioContext(
            portfolio_id=pid,
            portfolio_type=PortfolioType.PAPER,
            is_live_broker=False,
        )

    def create_live_zerodha_context(
        self, zerodha_account_id: str | None = None
    ) -> PortfolioContext:
        """Create an isolated live Zerodha portfolio context."""
        pid = PortfolioId.generate()
        return PortfolioContext(
            portfolio_id=pid,
            portfolio_type=PortfolioType.LIVE,
            is_live_broker=True,
        )

    def get_isolated_summary(
        self,
        paper_context: PortfolioContext,
        live_context: PortfolioContext,
        zerodha_portfolio_manager: ZerodhaPortfolioManager | None = None,
    ) -> dict[str, Any]:
        """
        Retrieves portfolio summaries for paper and live contexts separately, ensuring zero mixing.
        """
        paper_context.validate_isolation(target_is_live=False)
        live_context.validate_isolation(target_is_live=True)

        paper_summary = {
            "portfolio_id": str(paper_context.portfolio_id),
            "type": "PAPER",
            "holdings_count": len(self._paper_holdings.get(str(paper_context.portfolio_id), [])),
            "positions_count": len(self._paper_positions.get(str(paper_context.portfolio_id), [])),
        }

        live_summary = {
            "portfolio_id": str(live_context.portfolio_id),
            "type": "LIVE_ZERODHA",
            "holdings": (
                zerodha_portfolio_manager.get_holdings() if zerodha_portfolio_manager else []
            ),
            "positions": (
                zerodha_portfolio_manager.get_positions() if zerodha_portfolio_manager else {}
            ),
        }

        return {
            "paper": paper_summary,
            "live": live_summary,
        }
