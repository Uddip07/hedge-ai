"""
Unit tests for Market Data Engine providers, cache, mapper, and adapters.
"""

import unittest
from decimal import Decimal

from packages.domain.enums.market import ExchangeType, MarketSegment, Timeframe
from packages.domain.value_objects.identifiers import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.adapters.mock_market_data_adapter import (
    MockMarketDataAdapter,
)
from packages.infrastructure.market_data.cache import MarketDataCache
from packages.infrastructure.market_data.mapper import MarketDataMapper
from packages.infrastructure.market_data.models import (
    CorporateAction,
    MarketQuote,
    MarketStatusInfo,
)
from packages.infrastructure.market_data.providers import (
    MockMarketDataProvider,
    NSEMarketDataProvider,
    YahooMarketDataProvider,
)


class TestMarketDataEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker = Ticker("RELIANCE.NSE")

    def test_market_data_models_serialization(self) -> None:
        quote = MarketDataMapper.to_market_quote(self.ticker, "2500.00", "1.5", "100000")
        self.assertIsInstance(quote, MarketQuote)
        d = quote.to_dict()
        self.assertEqual(d["ticker"], "RELIANCE.NSE")
        self.assertEqual(d["price"], "2500.00")

        action = CorporateAction(
            ticker=self.ticker,
            action_type="DIVIDEND",
            record_date="2026-06-01",
            description="Dividend INR 10",
        )
        self.assertEqual(action.to_dict()["action_type"], "DIVIDEND")

        status_info = MarketStatusInfo(exchange=ExchangeType.NSE, is_open=True)
        self.assertTrue(status_info.to_dict()["is_open"])

    def test_mock_market_data_provider(self) -> None:
        provider = MockMarketDataProvider()
        quote = provider.get_quote(self.ticker)
        self.assertEqual(quote.ticker.full_symbol, "RELIANCE.NSE")
        self.assertGreater(quote.price.amount, Decimal("0.00"))

        from datetime import timedelta

        now = Timestamp.now_utc()
        start = Timestamp(value=now.value - timedelta(days=30))
        candles = provider.get_historical_ohlcv(self.ticker, Timeframe.DAY_1, start, now)
        self.assertIsInstance(candles, list)

        profile = provider.get_company_profile(self.ticker)
        self.assertIsNotNone(profile)
        if profile:
            self.assertTrue(len(profile.name) > 0)
            self.assertEqual(profile.sector, MarketSegment.LARGE_CAP)

        m_status = provider.get_market_status(ExchangeType.NSE)
        self.assertIsInstance(m_status.is_open, bool)

        actions = provider.get_corporate_actions(self.ticker)
        self.assertIsInstance(actions, list)

    def test_nse_and_yahoo_placeholder_providers(self) -> None:
        nse_provider = NSEMarketDataProvider()
        yahoo_provider = YahooMarketDataProvider()

        q_nse = nse_provider.get_quote(self.ticker)
        q_yahoo = yahoo_provider.get_quote(self.ticker)

        self.assertEqual(q_nse.ticker.full_symbol, "RELIANCE.NSE")
        self.assertEqual(q_yahoo.ticker.full_symbol, "RELIANCE.NSE")

    def test_market_data_cache(self) -> None:
        cache = MarketDataCache()
        self.assertIsNone(cache.get_quote(self.ticker))

        quote = MockMarketDataProvider().get_quote(self.ticker)
        cache.set_quote(self.ticker, quote)

        cached = cache.get_quote(self.ticker)
        self.assertIsNotNone(cached)
        cache.clear()
        self.assertIsNone(cache.get_quote(self.ticker))

    def test_mock_market_data_adapter(self) -> None:
        adapter = MockMarketDataAdapter()
        price = adapter.get_latest_price(self.ticker)
        self.assertGreater(price.amount, Decimal("0.00"))

        profile = adapter.get_company_profile(self.ticker)
        self.assertIsNotNone(profile)

        self.assertIsInstance(adapter.is_market_open(ExchangeType.NSE), bool)


if __name__ == "__main__":
    unittest.main()
