"""
Portfolio Domain Package for the Indian AI Hedge Fund Platform.

Consolidates Portfolio Aggregate Root, Holding, Position, Trade,
PortfolioSnapshot, PerformanceSnapshot, Allocation, and RebalancePlan.
"""

from packages.domain.portfolio.holding import Holding
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.portfolio.position import Position
from packages.domain.portfolio.rebalance import RebalancePlan
from packages.domain.portfolio.snapshot import (
    PerformanceSnapshot,
    PortfolioSnapshot,
)
from packages.domain.portfolio.trade import Trade
from packages.domain.value_objects.core.allocation import Allocation

__all__ = [
    "Portfolio",
    "Holding",
    "Position",
    "Trade",
    "PortfolioSnapshot",
    "PerformanceSnapshot",
    "Allocation",
    "RebalancePlan",
]
