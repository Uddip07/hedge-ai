"""
Metrics Value Objects Package for the Indian AI Hedge Fund Domain.

Consolidates RiskScore, ConfidenceScore, RecommendationScore, SharpeRatio, SortinoRatio,
Drawdown, Volatility, ATR, RSI, and MACD value objects.
"""

from packages.domain.value_objects.metrics.indicators import ATR, MACD, RSI
from packages.domain.value_objects.metrics.ratios import (
    Drawdown,
    SharpeRatio,
    SortinoRatio,
    Volatility,
)
from packages.domain.value_objects.metrics.scores import (
    ConfidenceScore,
    RecommendationScore,
    RiskScore,
)

__all__ = [
    # Scores
    "RiskScore",
    "ConfidenceScore",
    "RecommendationScore",
    # Ratios
    "SharpeRatio",
    "SortinoRatio",
    "Drawdown",
    "Volatility",
    # Indicators
    "ATR",
    "RSI",
    "MACD",
]
