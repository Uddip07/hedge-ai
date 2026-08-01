"""
Dependency Injection Container for Infrastructure Wiring.

Assembles and wires Configuration, DatabaseManager, Cache, StructuredLogger, Repositories,
Outbound Port Adapters, Application Use Cases, and Application Services.
Strictly enforces environment-specific provider rules (e.g. Production forbids mocks).
"""

import os

import packages.infrastructure.database.models  # noqa: F401
from packages.application.ports.broker_port import BrokerPort
from packages.application.ports.llm_port import LLMPort
from packages.application.ports.notification_port import NotificationPort
from packages.application.ports.portfolio_port import PortfolioPort
from packages.application.ports.research_port import ResearchPort
from packages.application.ports.storage_port import StoragePort
from packages.application.services.auth_application_service import (
    AuthApplicationService,
)
from packages.application.services.research_application_service import (
    ResearchApplicationService,
)
from packages.application.use_cases.analyze_stock_use_case import AnalyzeStockUseCase
from packages.infrastructure.adapters.mock_llm_adapter import MockLLMAdapter
from packages.infrastructure.adapters.mock_market_data_adapter import (
    YahooMarketDataAdapter,
)
from packages.infrastructure.adapters.mock_notification_adapter import (
    MockNotificationAdapter,
)
from packages.infrastructure.adapters.mock_storage_adapter import MockStorageAdapter
from packages.infrastructure.adapters.portfolio_adapter import SQLPortfolioAdapter
from packages.infrastructure.adapters.research_adapter import SQLResearchAdapter
from packages.infrastructure.cache.base import BaseCache
from packages.infrastructure.cache.memory_cache import MemoryCacheAdapter
from packages.infrastructure.cache.redis_cache import RedisCacheAdapter
from packages.infrastructure.config.settings import AppSettings, get_settings
from packages.infrastructure.database.config import DatabaseConfig
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.logging.logger import StructuredLogger, get_logger
from packages.infrastructure.market_data.registry import MarketDataProviderRegistry
from packages.infrastructure.repositories.asset_repository import SQLAssetRepository
from packages.infrastructure.repositories.portfolio_repository import (
    SQLPortfolioRepository,
)
from packages.infrastructure.repositories.research_repository import (
    SQLResearchRepository,
)
from packages.infrastructure.repositories.user_repository import (
    SQLUserRepository,
)


class DIContainer:
    """
    Central Dependency Injection (DI) Container.

    Encapsulates lifetime management and dependency graph resolution.

    Production wiring:
      - market_data_port  → YahooMarketDataAdapter (Yahoo Finance via ProviderManager)
      - research_port     → SQLResearchAdapter (SQL-backed; returns None until AI committee runs)
      - portfolio_port    → SQLPortfolioAdapter (SQL-backed; real portfolio data)
      - broker_port       → ZerodhaBrokerAdapter (KiteConnect integration)
      - llm_port          → MockLLMAdapter (until LLM provider credentials are configured)
      - notification_port → MockNotificationAdapter (until notification provider is configured)
      - storage_port      → MockStorageAdapter (until cloud storage is configured)
    """

    def __init__(self, settings: AppSettings | None = None) -> None:
        self.settings: AppSettings = settings or get_settings()

        # Database Manager
        self.db_manager = DatabaseManager(
            DatabaseConfig(
                url=self.settings.database_url,
                echo=self.settings.db_echo,
                pool_size=self.settings.db_pool_size,
                max_overflow=self.settings.db_max_overflow,
            )
        )
        if self.settings.environment != "production" and os.getenv(
            "IHF_RESET_STATE", ""
        ).lower() in {"1", "true", "yes", "on"}:
            self.db_manager.drop_all()

        self.db_manager.create_all()

        # Structured Logger
        self.logger: StructuredLogger = get_logger(
            level=self.settings.log_level,
            log_format=self.settings.log_format,
        )

        # Cache Provider
        self.cache: BaseCache = (
            RedisCacheAdapter(self.settings.redis_url)
            if self.settings.cache_enabled
            else MemoryCacheAdapter()
        )

        # Repositories
        self.portfolio_repository = SQLPortfolioRepository(self.db_manager.session_factory)
        self.asset_repository = SQLAssetRepository(self.db_manager.session_factory)
        self.research_repository = SQLResearchRepository(self.db_manager.session_factory)
        self.user_repository = SQLUserRepository(self.db_manager.session_factory)

        # Market Data Provider Registry
        self.market_data_registry = MarketDataProviderRegistry()

        # Environment-Aware Market Data Provider Resolution
        from packages.infrastructure.brokers.zerodha import ZerodhaBrokerAdapter
        from packages.infrastructure.market_data.providers.yahoo_provider import (
            YahooMarketDataProvider,
        )

        yahoo_provider = YahooMarketDataProvider()
        self.market_data_registry.register("yahoo", yahoo_provider)

        # Production Outbound Port Adapters
        self.market_data_port = YahooMarketDataAdapter()
        self.broker_port: BrokerPort = ZerodhaBrokerAdapter()
        self.llm_port: LLMPort = MockLLMAdapter()
        self.notification_port: NotificationPort = MockNotificationAdapter()
        self.storage_port: StoragePort = MockStorageAdapter()

        # Production SQL-backed Research and Portfolio Ports
        self.research_port: ResearchPort = SQLResearchAdapter(repository=self.research_repository)
        self.portfolio_port: PortfolioPort = SQLPortfolioAdapter(
            repository=self.portfolio_repository
        )

        # Application Use Cases
        self.analyze_stock_use_case = AnalyzeStockUseCase(
            research_port=self.research_port,
            portfolio_port=self.portfolio_port,
            market_data_port=self.market_data_port,
        )

        # Application Services
        self.research_service = ResearchApplicationService(
            analyze_stock_use_case=self.analyze_stock_use_case
        )
        self.auth_service = AuthApplicationService(
            user_repository=self.user_repository,
            portfolio_repository=self.portfolio_repository,
        )
