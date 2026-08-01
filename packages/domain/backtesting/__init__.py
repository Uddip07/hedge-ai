"""
Backtesting Domain Package for the Indian AI Hedge Fund Platform.

Consolidates Backtest Aggregate Root, BacktestRun, BacktestMetrics, TradeLog, EquityCurve, and BacktestResult.
"""

from packages.domain.backtesting.backtest import Backtest, BacktestRun
from packages.domain.backtesting.logs import EquityCurve, TradeLog
from packages.domain.backtesting.metrics import BacktestMetrics, BacktestResult

__all__ = [
    "Backtest",
    "BacktestRun",
    "BacktestMetrics",
    "TradeLog",
    "EquityCurve",
    "BacktestResult",
]
