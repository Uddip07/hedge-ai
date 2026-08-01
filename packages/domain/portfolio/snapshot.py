"""
PortfolioSnapshot and PerformanceSnapshot Value Objects for the Indian AI Hedge Fund Domain.

Provides historical point-in-time equity snapshots and performance metric evaluations.
Supports Live Trading, Paper Trading, Backtesting, and Historical Analytics.
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.utils.validation import to_decimal
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.percentage import Percentage
from packages.domain.value_objects.metrics.ratios import (
    Drawdown,
    SharpeRatio,
    SortinoRatio,
    Volatility,
)
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, slots=True)
class PortfolioSnapshot:
    """
    Immutable value object capturing a portfolio's complete financial state at a single point in time.

    Attributes:
        portfolio_id (uuid.UUID): ID of the portfolio.
        timestamp (Timestamp): Point-in-time timestamp of the snapshot.
        total_equity (Money): Total equity valuation (cash + market value of holdings).
        cash_balance (Money): Available uninvested cash balance.
        invested_capital (Money): Market value of open holding positions.
        unrealized_pnl (Money): Total unrealized PnL across all open holdings.
        realized_pnl (Money): Total cumulative realized PnL.
        holding_count (int): Total number of open holding positions.
    """

    portfolio_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: Timestamp = field(default_factory=Timestamp.now_utc)
    total_equity: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    cash_balance: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    invested_capital: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    unrealized_pnl: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    realized_pnl: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    holding_count: int = 0
    holdings_count: int = 0
    positions_count: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.portfolio_id, uuid.UUID):
            object.__setattr__(self, "portfolio_id", uuid.UUID(str(self.portfolio_id)))
        if not isinstance(self.timestamp, Timestamp):
            object.__setattr__(self, "timestamp", Timestamp(self.timestamp))
        if self.holdings_count > 0 and self.holding_count == 0:
            object.__setattr__(self, "holding_count", self.holdings_count)

    def to_dict(self) -> dict[str, Any]:
        """Serialize PortfolioSnapshot to dictionary representation."""
        return {
            "portfolio_id": str(self.portfolio_id),
            "timestamp": self.timestamp.isoformat(),
            "total_equity": self.total_equity.to_dict(),
            "cash_balance": self.cash_balance.to_dict(),
            "invested_capital": self.invested_capital.to_dict(),
            "unrealized_pnl": self.unrealized_pnl.to_dict(),
            "realized_pnl": self.realized_pnl.to_dict(),
            "holding_count": self.holding_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PortfolioSnapshot":
        """Deserialize dictionary to PortfolioSnapshot."""
        return cls(
            portfolio_id=(
                uuid.UUID(data["portfolio_id"]) if data.get("portfolio_id") else uuid.uuid4()
            ),
            timestamp=Timestamp.from_isoformat(data["timestamp"]),
            total_equity=Money.from_dict(data["total_equity"]),
            cash_balance=Money.from_dict(data["cash_balance"]),
            invested_capital=Money.from_dict(data["invested_capital"]),
            unrealized_pnl=Money.from_dict(data["unrealized_pnl"]),
            realized_pnl=Money.from_dict(data["realized_pnl"]),
            holding_count=int(data.get("holding_count", data.get("holdings_count", 0))),
        )


@dataclass(frozen=True, slots=True)
class PerformanceSnapshot:
    """
    Immutable value object holding aggregated performance metrics for a portfolio or strategy.

    Attributes:
        timestamp (Timestamp): Valuation timestamp.
        total_return (Percentage): Total cumulative return percentage.
        cagr (Percentage): Compound Annual Growth Rate.
        sharpe_ratio (SharpeRatio): Annualized Sharpe Ratio.
        sortino_ratio (SortinoRatio): Annualized Sortino Ratio.
        max_drawdown (Drawdown): Maximum historical peak-to-trough drawdown.
        volatility (Volatility): Annualized return volatility.
        win_rate (Percentage): Win rate percentage across executed trades.
    """

    timestamp: Timestamp
    total_return: Percentage
    cagr: Percentage
    sharpe_ratio: SharpeRatio
    sortino_ratio: SortinoRatio
    max_drawdown: Drawdown
    volatility: Volatility
    win_rate: Percentage

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, Timestamp):
            object.__setattr__(self, "timestamp", Timestamp(self.timestamp))
        if not isinstance(self.total_return, Percentage):
            object.__setattr__(self, "total_return", Percentage(to_decimal(self.total_return)))
        if not isinstance(self.cagr, Percentage):
            object.__setattr__(self, "cagr", Percentage(to_decimal(self.cagr)))
        if not isinstance(self.sharpe_ratio, SharpeRatio):
            object.__setattr__(self, "sharpe_ratio", SharpeRatio(to_decimal(self.sharpe_ratio)))
        if not isinstance(self.sortino_ratio, SortinoRatio):
            object.__setattr__(self, "sortino_ratio", SortinoRatio(to_decimal(self.sortino_ratio)))
        if not isinstance(self.max_drawdown, Drawdown):
            object.__setattr__(self, "max_drawdown", Drawdown.from_value(self.max_drawdown))
        if not isinstance(self.volatility, Volatility):
            object.__setattr__(self, "volatility", Volatility.from_value(self.volatility))
        if not isinstance(self.win_rate, Percentage):
            object.__setattr__(self, "win_rate", Percentage(to_decimal(self.win_rate)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize PerformanceSnapshot to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_return": self.total_return.to_dict(),
            "cagr": self.cagr.to_dict(),
            "sharpe_ratio": self.sharpe_ratio.to_dict(),
            "sortino_ratio": self.sortino_ratio.to_dict(),
            "max_drawdown": self.max_drawdown.to_dict(),
            "volatility": self.volatility.to_dict(),
            "win_rate": self.win_rate.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PerformanceSnapshot":
        """Deserialize dictionary to PerformanceSnapshot."""
        return cls(
            timestamp=Timestamp.from_isoformat(data["timestamp"]),
            total_return=Percentage.from_dict(data["total_return"]),
            cagr=Percentage.from_dict(data["cagr"]),
            sharpe_ratio=SharpeRatio.from_dict(data["sharpe_ratio"]),
            sortino_ratio=SortinoRatio.from_dict(data["sortino_ratio"]),
            max_drawdown=Drawdown.from_dict(data["max_drawdown"]),
            volatility=Volatility.from_dict(data["volatility"]),
            win_rate=Percentage.from_dict(data["win_rate"]),
        )
