"""
BacktestMetrics and BacktestResult Models for the Indian AI Hedge Fund Platform.

Provides performance analytics summary metrics and complete backtest simulation execution results.
Pure domain value objects with zero infrastructure dependencies.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.backtesting.logs import EquityCurve, TradeLog
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.percentage import Percentage
from packages.domain.value_objects.metrics.ratios import (
    Drawdown,
    SharpeRatio,
    SortinoRatio,
    Volatility,
)


@dataclass(frozen=True, slots=True)
class BacktestMetrics:
    """
    Immutable value object consolidating quantitative backtest performance metrics.

    Attributes:
        cagr (Percentage): Compound Annual Growth Rate percentage.
        sharpe_ratio (SharpeRatio): Annualized risk-adjusted Sharpe ratio.
        sortino_ratio (SortinoRatio): Annualized downside risk-adjusted Sortino ratio.
        max_drawdown (Drawdown): Maximum peak-to-trough equity drawdown percentage.
        volatility (Volatility): Annualized equity return volatility percentage.
        win_rate (Percentage): Winning trade ratio percentage.
        profit_factor (Decimal): Gross profits to gross losses ratio.
        calmar_ratio (Decimal): CAGR to Max Drawdown ratio.
        total_trades (int): Total count of trades executed in backtest.
    """

    cagr: Percentage
    sharpe_ratio: SharpeRatio
    sortino_ratio: SortinoRatio
    max_drawdown: Drawdown
    volatility: Volatility
    win_rate: Percentage
    profit_factor: Decimal = Decimal("1.0")
    calmar_ratio: Decimal = Decimal("0.0")
    total_trades: int = 0

    def __post_init__(self) -> None:
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
        object.__setattr__(self, "profit_factor", to_decimal(self.profit_factor))
        object.__setattr__(self, "calmar_ratio", to_decimal(self.calmar_ratio))

    def to_dict(self) -> dict[str, Any]:
        """Serialize BacktestMetrics to dictionary."""
        return {
            "cagr": self.cagr.to_dict(),
            "sharpe_ratio": self.sharpe_ratio.to_dict(),
            "sortino_ratio": self.sortino_ratio.to_dict(),
            "max_drawdown": self.max_drawdown.to_dict(),
            "volatility": self.volatility.to_dict(),
            "win_rate": self.win_rate.to_dict(),
            "profit_factor": str(self.profit_factor),
            "calmar_ratio": str(self.calmar_ratio),
            "total_trades": self.total_trades,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BacktestMetrics":
        """Deserialize dictionary to BacktestMetrics."""
        return cls(
            cagr=Percentage.from_dict(data["cagr"]),
            sharpe_ratio=SharpeRatio.from_dict(data["sharpe_ratio"]),
            sortino_ratio=SortinoRatio.from_dict(data["sortino_ratio"]),
            max_drawdown=Drawdown.from_dict(data["max_drawdown"]),
            volatility=Volatility.from_dict(data["volatility"]),
            win_rate=Percentage.from_dict(data["win_rate"]),
            profit_factor=Decimal(str(data.get("profit_factor", "1.0"))),
            calmar_ratio=Decimal(str(data.get("calmar_ratio", "0.0"))),
            total_trades=int(data.get("total_trades", 0)),
        )


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """
    Immutable value object encapsulating complete backtest execution output payload.

    Attributes:
        metrics (BacktestMetrics): Aggregated risk/return metrics.
        equity_curve (EquityCurve): Time series equity curve.
        trade_log (TradeLog): Executed trades log.
        final_equity (Money): Ending equity value.
        total_return_pct (Percentage): Net percentage return.
    """

    metrics: BacktestMetrics
    equity_curve: EquityCurve
    trade_log: TradeLog
    final_equity: Money
    total_return_pct: Percentage

    def __post_init__(self) -> None:
        if not isinstance(self.metrics, BacktestMetrics):
            raise ValueError("metrics must be a valid BacktestMetrics instance.")
        if not isinstance(self.equity_curve, EquityCurve):
            raise ValueError("equity_curve must be a valid EquityCurve instance.")
        if not isinstance(self.trade_log, TradeLog):
            raise ValueError("trade_log must be a valid TradeLog instance.")
        if not isinstance(self.final_equity, Money):
            object.__setattr__(self, "final_equity", Money(self.final_equity))
        if not isinstance(self.total_return_pct, Percentage):
            object.__setattr__(
                self, "total_return_pct", Percentage(to_decimal(self.total_return_pct))
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize BacktestResult to dictionary."""
        return {
            "metrics": self.metrics.to_dict(),
            "equity_curve": self.equity_curve.to_dict(),
            "trade_log": self.trade_log.to_dict(),
            "final_equity": self.final_equity.to_dict(),
            "total_return_pct": self.total_return_pct.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BacktestResult":
        """Deserialize dictionary to BacktestResult."""
        return cls(
            metrics=BacktestMetrics.from_dict(data["metrics"]),
            equity_curve=EquityCurve.from_dict(data["equity_curve"]),
            trade_log=TradeLog.from_dict(data["trade_log"]),
            final_equity=Money.from_dict(data["final_equity"]),
            total_return_pct=Percentage.from_dict(data["total_return_pct"]),
        )
