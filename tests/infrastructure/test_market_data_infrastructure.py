"""
Unit tests for generic Market Data Infrastructure components:
TickerNormalizer, ProviderMetadata, MarketDataProviderRegistry, RetryPolicy, and Telemetry.
"""

import unittest

from packages.domain.enums.market import ExchangeType
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.exceptions import (
    FeatureNotSupportedError,
    ProviderCapabilityError,
    ProviderConnectionError,
)
from packages.infrastructure.market_data.metadata import ProviderMetadata
from packages.infrastructure.market_data.normalizers.ticker import TickerNormalizer
from packages.infrastructure.market_data.providers.mock_provider import (
    MockMarketDataProvider,
)
from packages.infrastructure.market_data.registry import MarketDataProviderRegistry
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class TestMarketDataInfrastructure(unittest.TestCase):
    def test_ticker_normalizer(self) -> None:
        ticker_nse = Ticker("RELIANCE.NSE")
        self.assertEqual(TickerNormalizer.to_provider_symbol(ticker_nse, "yahoo"), "RELIANCE.NS")
        self.assertEqual(TickerNormalizer.to_provider_symbol(ticker_nse, "yfinance"), "RELIANCE.NS")

        ticker_bse = Ticker("INFY.BSE")
        self.assertEqual(TickerNormalizer.to_provider_symbol(ticker_bse, "yahoo"), "INFY.BO")

        ticker_nyse = Ticker("AAPL.NYSE")
        self.assertEqual(TickerNormalizer.to_provider_symbol(ticker_nyse, "yahoo"), "AAPL")

        # Reverse normalizer
        rev_ticker = TickerNormalizer.from_provider_symbol("SBIN.NS")
        self.assertEqual(rev_ticker.full_symbol, "SBIN.NSE")

    def test_provider_metadata(self) -> None:
        meta = ProviderMetadata(
            provider_name="TestProvider",
            provider_version="1.0.0",
            supported_markets=["IN"],
            supported_exchanges=[ExchangeType.NSE],
        )
        self.assertEqual(meta.provider_name, "TestProvider")
        self.assertTrue(meta.supports_quotes)
        self.assertFalse(meta.supports_options)
        self.assertEqual(meta.to_dict()["provider_name"], "TestProvider")

    def test_market_data_provider_registry(self) -> None:
        registry = MarketDataProviderRegistry()
        mock_prov = MockMarketDataProvider()

        meta = ProviderMetadata(provider_name="Mock", provider_version="1.0.0")
        registry.register("mock", mock_prov, meta)

        self.assertIn("mock", registry.list_providers())
        retrieved = registry.lookup("mock")
        self.assertEqual(retrieved, mock_prov)

        retrieved_meta = registry.provider_metadata("mock")
        self.assertEqual(retrieved_meta.provider_name, "Mock")

        registry.unregister("mock")
        self.assertNotIn("mock", registry.list_providers())
        with self.assertRaises(ProviderCapabilityError):
            registry.lookup("mock")

    def test_retry_policy_transient_error(self) -> None:
        policy = RetryPolicy(max_retries=2, initial_delay_sec=0.01)
        counter = {"attempts": 0}

        def failing_transient() -> str:
            counter["attempts"] += 1
            if counter["attempts"] < 2:
                raise ProviderConnectionError("Transient network failure")
            return "SUCCESS"

        res = policy.execute(failing_transient)
        self.assertEqual(res, "SUCCESS")
        self.assertEqual(counter["attempts"], 2)

    def test_retry_policy_non_transient_fail_fast(self) -> None:
        policy = RetryPolicy(max_retries=3, initial_delay_sec=0.01)
        counter = {"attempts": 0}

        def failing_validation() -> None:
            counter["attempts"] += 1
            raise FeatureNotSupportedError("Feature unsupported")

        with self.assertRaises(FeatureNotSupportedError):
            policy.execute(failing_validation)
        # Must fail fast without retrying
        self.assertEqual(counter["attempts"], 1)

    def test_market_data_telemetry(self) -> None:
        telemetry = MarketDataTelemetry()
        with TelemetryTimer() as timer:
            pass

        self.assertGreaterEqual(timer.latency_ms, 0.0)

        telemetry.record_event(
            provider="Yahoo",
            operation="get_quote",
            ticker="RELIANCE.NSE",
            latency_ms=12.5,
            cache_hit=False,
            success=True,
        )

        records = telemetry.get_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].provider, "Yahoo")
        self.assertEqual(records[0].ticker, "RELIANCE.NSE")
        self.assertTrue(records[0].success)


if __name__ == "__main__":
    unittest.main()
