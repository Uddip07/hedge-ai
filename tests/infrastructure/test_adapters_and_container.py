"""
Unit tests for Mock Adapters and DIContainer dependency injection wiring.
"""

import unittest

from packages.application.dto.analyze_stock_dto import AnalyzeStockResultDTO
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.adapters import (
    MockBrokerAdapter,
    MockLLMAdapter,
    MockMarketDataAdapter,
    MockNotificationAdapter,
    MockStorageAdapter,
)
from packages.infrastructure.dependency_injection import DIContainer


class TestAdaptersAndContainer(unittest.TestCase):
    def test_mock_adapters(self) -> None:
        market_adapter = MockMarketDataAdapter()
        p = market_adapter.get_latest_price(Ticker("RELIANCE.NSE"))
        self.assertGreater(p.money.amount, 0)

        broker_adapter = MockBrokerAdapter()
        self.assertIsNotNone(broker_adapter)

        llm_adapter = MockLLMAdapter()
        res = llm_adapter.generate_structured_output("Analyze stock", {})
        self.assertEqual(res["status"], "SUCCESS")

        notif_adapter = MockNotificationAdapter()
        self.assertTrue(notif_adapter.send_alert("Title", "Message"))

        storage_adapter = MockStorageAdapter()
        key = storage_adapter.store_file("test.txt", b"hello")
        self.assertEqual(storage_adapter.retrieve_file(key), b"hello")

    def test_di_container_wiring(self) -> None:
        container = DIContainer()

        self.assertIsNotNone(container.settings)
        self.assertIsNotNone(container.db_manager)
        self.assertIsNotNone(container.logger)
        self.assertIsNotNone(container.cache)
        self.assertIsNotNone(container.portfolio_repository)
        self.assertIsNotNone(container.asset_repository)
        self.assertIsNotNone(container.research_repository)
        self.assertIsNotNone(container.market_data_port)
        self.assertIsNotNone(container.broker_port)
        self.assertIsNotNone(container.llm_port)
        self.assertIsNotNone(container.notification_port)
        self.assertIsNotNone(container.storage_port)
        self.assertIsNotNone(container.research_port)
        self.assertIsNotNone(container.portfolio_port)
        self.assertIsNotNone(container.analyze_stock_use_case)
        self.assertIsNotNone(container.research_service)

        # Execute end-to-end stock analysis via wired DI container service
        res = container.research_service.analyze_stock(ticker_symbol="INFY.NSE")
        self.assertIsInstance(res, AnalyzeStockResultDTO)
        self.assertEqual(res.ticker, "INFY.NSE")


if __name__ == "__main__":
    unittest.main()
