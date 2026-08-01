"""
Infrastructure Adapters Package.

Exports both production SQL-backed adapters and test/offline mock adapters
that implement Application Outbound Ports.
"""

from packages.infrastructure.adapters.mock_broker_adapter import MockBrokerAdapter
from packages.infrastructure.adapters.mock_llm_adapter import MockLLMAdapter
from packages.infrastructure.adapters.mock_market_data_adapter import (
    MockMarketDataAdapter,
    YahooMarketDataAdapter,
)
from packages.infrastructure.adapters.mock_notification_adapter import (
    MockNotificationAdapter,
)
from packages.infrastructure.adapters.mock_portfolio_adapter import (
    MockPortfolioAdapter,
)
from packages.infrastructure.adapters.mock_research_adapter import MockResearchAdapter
from packages.infrastructure.adapters.mock_storage_adapter import MockStorageAdapter
from packages.infrastructure.adapters.portfolio_adapter import SQLPortfolioAdapter
from packages.infrastructure.adapters.research_adapter import SQLResearchAdapter

__all__ = [
    # Production adapters
    "SQLPortfolioAdapter",
    "SQLResearchAdapter",
    "YahooMarketDataAdapter",
    # Mock/test adapters
    "MockBrokerAdapter",
    "MockLLMAdapter",
    "MockMarketDataAdapter",
    "MockNotificationAdapter",
    "MockPortfolioAdapter",
    "MockResearchAdapter",
    "MockStorageAdapter",
]
