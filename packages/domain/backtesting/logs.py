"""
TradeLog and EquityCurve Value Objects for the Indian AI Hedge Fund Platform.

Provides TradeLog and EquityCurve tracking models for historical backtesting simulations.
Pure domain models with zero infrastructure dependencies.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.portfolio.trade import Trade
from packages.domain.utils.math import calculate_drawdown, calculate_return
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.percentage import Percentage
from packages.domain.value_objects.metrics.ratios import Drawdown


@dataclass(frozen=True, slots=True)
class TradeLog:
    """
    Immutable value object encapsulating executed trades ledger during backtest.

    Attributes:
        trades (List[Trade]): Ordered list of executed trades.
    """

    trades: list[Trade] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.trades, list):
            raise ValidationError("TradeLog trades must be a list.")

    @property
    def total_trades(self) -> int:
        """Return total number of executed trades."""
        return len(self.trades)

    @property
    def total_trades_count(self) -> int:
        """Alias for total_trades property."""
        return len(self.trades)

    @property
    def winning_trades(self) -> int:
        """Return count of profitable trades."""
        return sum(1 for t in self.trades if t.net_amount.amount > Decimal("0"))

    @property
    def losing_trades(self) -> int:
        """Return count of unprofitable trades."""
        return sum(1 for t in self.trades if t.net_amount.amount < Decimal("0"))

    @property
    def total_frictions(self) -> Money:
        """Return sum of total frictions (fees + taxes) across all trades."""
        if not self.trades:
            return Money(Decimal("0.00"))
        tot = sum((t.total_frictions.amount for t in self.trades), Decimal("0.00"))
        return Money(tot, currency=self.trades[0].fee.currency)

    @property
    def win_rate(self) -> Percentage:
        """Calculate win rate percentage."""
        if self.total_trades == 0:
            return Percentage(Decimal("0.0"))
        ratio = Decimal(str(self.winning_trades)) / Decimal(str(self.total_trades))
        return Percentage(ratio * Decimal("100"))

    def to_dict(self) -> dict[str, Any]:
        """Serialize TradeLog to dictionary."""
        return {
            "trades": [t.to_dict() for t in self.trades],
            "total_trades": self.total_trades,
            "win_rate": self.win_rate.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradeLog":
        """Deserialize dictionary to TradeLog."""
        trades = [Trade.from_dict(t) for t in data.get("trades", [])]
        return cls(trades=trades)


@dataclass(frozen=True, slots=True)
class EquityCurve:
    """
    Immutable value object representing portfolio valuation over time during backtest.

    Attributes:
        snapshots (List[PortfolioSnapshot]): Time-ordered portfolio snapshots.
    """

    snapshots: list[PortfolioSnapshot] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.snapshots, list):
            raise ValidationError("EquityCurve snapshots must be a list.")

    @property
    def initial_equity(self) -> Money:
        """Return starting portfolio equity."""
        return self.snapshots[0].total_equity if self.snapshots else Money(Decimal("0.00"))

    @property
    def final_equity(self) -> Money:
        """Return ending portfolio equity."""
        return self.snapshots[-1].total_equity if self.snapshots else Money(Decimal("0.00"))

    @property
    def peak_equity(self) -> Money:
        """Return maximum portfolio equity achieved."""
        if not self.snapshots:
            return Money(Decimal("0.00"))
        return max(self.snapshots, key=lambda s: s.total_equity.amount).total_equity

    @property
    def total_return_pct(self) -> Percentage:
        """Calculate total cumulative return percentage across the curve."""
        if not self.snapshots:
            return Percentage(Decimal("0.0"))
        ret_val = calculate_return(self.initial_equity.amount, self.final_equity.amount)
        return Percentage(ret_val)

    @property
    def max_drawdown(self) -> Drawdown:
        """Calculate maximum peak-to-trough drawdown across the curve."""
        if not self.snapshots:
            return Drawdown.from_value(Decimal("0.0"))

        peak_amt = self.snapshots[0].total_equity.amount
        max_dd_val = Decimal("0.0")

        for s in self.snapshots:
            eq_amt = s.total_equity.amount
            if eq_amt > peak_amt:
                peak_amt = eq_amt
            dd_val = calculate_drawdown(eq_amt, peak_amt)
            if dd_val > max_dd_val:
                max_dd_val = dd_val

        return Drawdown.from_value(max_dd_val)

    def to_dict(self) -> dict[str, Any]:
        """Serialize EquityCurve to dictionary."""
        return {
            "snapshots": [s.to_dict() for s in self.snapshots],
            "initial_equity": self.initial_equity.to_dict(),
            "final_equity": self.final_equity.to_dict(),
            "peak_equity": self.peak_equity.to_dict(),
            "total_return_pct": self.total_return_pct.to_dict(),
            "max_drawdown": self.max_drawdown.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EquityCurve":
        """Deserialize dictionary to EquityCurve."""
        snapshots = [PortfolioSnapshot.from_dict(s) for s in data.get("snapshots", [])]
        return cls(snapshots=snapshots)
