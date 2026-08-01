"""
Risk & Performance Enums for the Indian AI Hedge Fund Domain.

Defines risk severity levels, risk measurement metrics (VaR, CVaR, Drawdown),
and portfolio performance ratios.
"""

from enum import StrEnum


class RiskLevel(StrEnum):
    """
    Risk evaluation severity levels for trades, mandates, and portfolios.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNACCEPTABLE = "UNACCEPTABLE"

    def severity_rank(self) -> int:
        """Return an integer rank from 1 (lowest risk) to 5 (highest risk)."""
        ranks = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
            RiskLevel.UNACCEPTABLE: 5,
        }
        return ranks[self]

    def requires_circuit_breaker(self) -> bool:
        """Return True if the risk level requires automatic trading halt/kill switch."""
        return self in {RiskLevel.CRITICAL, RiskLevel.UNACCEPTABLE}


class RiskMetric(StrEnum):
    """
    Risk metric indicators used for portfolio risk assessments and mandate compliance.
    """

    VAR_95 = "VAR_95"
    VAR_99 = "VAR_99"
    CVAR_95 = "CVAR_95"
    MAX_DRAWDOWN = "MAX_DRAWDOWN"
    VOLATILITY = "VOLATILITY"
    BETA = "BETA"
    SHARPE = "SHARPE"
    SORTINO = "SORTINO"
    LEVERAGE = "LEVERAGE"
    CONCENTRATION = "CONCENTRATION"

    def is_tail_risk_metric(self) -> bool:
        """Return True if the metric measures extreme tail losses."""
        return self in {
            RiskMetric.VAR_95,
            RiskMetric.VAR_99,
            RiskMetric.CVAR_95,
            RiskMetric.MAX_DRAWDOWN,
        }


class PerformanceMetric(StrEnum):
    """
    Quantitative performance metrics for backtests, paper trading, and live portfolios.
    """

    CAGR = "CAGR"
    SHARPE_RATIO = "SHARPE_RATIO"
    SORTINO_RATIO = "SORTINO_RATIO"
    ALPHA = "ALPHA"
    BETA = "BETA"
    MAX_DRAWDOWN = "MAX_DRAWDOWN"
    WIN_RATE = "WIN_RATE"
    PROFIT_FACTOR = "PROFIT_FACTOR"
    CALMAR_RATIO = "CALMAR_RATIO"

    def is_risk_adjusted(self) -> bool:
        """Return True if the metric measures risk-adjusted return performance."""
        return self in {
            PerformanceMetric.SHARPE_RATIO,
            PerformanceMetric.SORTINO_RATIO,
            PerformanceMetric.ALPHA,
            PerformanceMetric.CALMAR_RATIO,
        }
