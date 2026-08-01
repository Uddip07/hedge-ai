"""
Domain Repositories Package for the Indian AI Hedge Fund Platform.

Consolidates all abstract repository interfaces for domain Aggregate Roots and Entities.
Pure domain interfaces with zero infrastructure dependencies.
"""

from packages.domain.repositories.asset_repository import AssetRepository
from packages.domain.repositories.backtest_repository import BacktestRepository
from packages.domain.repositories.broker_repository import BrokerAccountRepository
from packages.domain.repositories.company_repository import CompanyRepository
from packages.domain.repositories.knowledge_repository import KnowledgeBaseRepository
from packages.domain.repositories.portfolio_repository import PortfolioRepository
from packages.domain.repositories.prompt_repository import PromptRepository
from packages.domain.repositories.research_repository import ResearchReportRepository
from packages.domain.repositories.strategy_repository import StrategyRepository
from packages.domain.repositories.user_repository import UserRepository

__all__ = [
    "CompanyRepository",
    "AssetRepository",
    "PortfolioRepository",
    "BrokerAccountRepository",
    "StrategyRepository",
    "ResearchReportRepository",
    "KnowledgeBaseRepository",
    "BacktestRepository",
    "PromptRepository",
    "UserRepository",
]
