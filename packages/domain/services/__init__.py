"""
Domain Services Package for the Indian AI Hedge Fund Platform.

Consolidates stateless domain calculator services:
PortfolioCalculator, RiskCalculator, ConsensusCalculator, RecommendationAggregator,
DrawdownCalculator, SharpeCalculator, and ReturnCalculator.
"""

from packages.domain.services.consensus_calculator import ConsensusCalculator
from packages.domain.services.drawdown_calculator import DrawdownCalculator
from packages.domain.services.portfolio_calculator import PortfolioCalculator
from packages.domain.services.recommendation_aggregator import RecommendationAggregator
from packages.domain.services.return_calculator import ReturnCalculator
from packages.domain.services.risk_calculator import RiskCalculator
from packages.domain.services.sharpe_calculator import SharpeCalculator

__all__ = [
    "PortfolioCalculator",
    "RiskCalculator",
    "ConsensusCalculator",
    "RecommendationAggregator",
    "DrawdownCalculator",
    "SharpeCalculator",
    "ReturnCalculator",
]
