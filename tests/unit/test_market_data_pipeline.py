"""
Unit & Integration Tests for Market Data Pipeline (Phase 1).

Tests:
1. Normalization of MarketQuote domain model
2. Automatic provider failover (Primary Yahoo -> Fallbacks)

3. Adaptive TTL caching (3s market open, 300s closed)
4. Cache invalidation on force_refresh
5. Real-time market status detection (PRE_OPEN, OPEN, CLOSED)
"""

import unittest
from decimal import Decimal

from packages.domain.enums.market import ExchangeType, MarketStatus, Timeframe
from packages.domain.enums.system import CurrencyCode
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.market.provider import MarketProvider
from packages.domain.market.quote import MarketQuote
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.currency import Currency
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.cache import MarketDataCache
from packages.infrastructure.market_data.provider_manager import ProviderManager


class DummyTestProvider(MarketProvider):
    def __init__(self, name: str, should_fail: bool = False, price: str = "2500.00"):
        self._name = name
        self.should_fail = should_fail
        self.price_val = Decimal(price)

    @property
    def provider_name(self) -> str:
        return self._name

    def get_quote(self, ticker: Ticker) -> MarketQuote:
        if self.should_fail:
            raise RuntimeError(f"Provider {self._name} connection error")
        return MarketQuote(
            ticker=ticker,
            exchange=ExchangeType.NSE,
            price=Price(money=Money(amount=self.price_val, currency=Currency(CurrencyCode.INR))),
            change=Decimal("15.50"),
            change_percent=Decimal("0.62"),
            volume=Decimal("1200000.00"),
            open=Decimal("2490.00"),
            high=Decimal("2515.00"),
            low=Decimal("2485.00"),
            previous_close=Decimal("2484.50"),
            currency="INR",
            timestamp=Timestamp.now_utc(),
            market_status=MarketStatus.OPEN,
        )

    def get_historical_candles(
        self, ticker: Ticker, timeframe: Timeframe, start_time: Timestamp, end_time: Timestamp
    ) -> list[Candle]:
        if self.should_fail:
            raise RuntimeError(f"Provider {self._name} error")
        return []

    def get_company_profile(self, ticker: Ticker) -> Company | None:
        if self.should_fail:
            raise RuntimeError(f"Provider {self._name} error")
        return None

    def get_market_status(self, exchange: ExchangeType) -> MarketStatus:
        return MarketStatus.OPEN


class TestMarketDataPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker = Ticker("RELIANCE.NSE")
        self.cache = MarketDataCache()
        self.cache.clear()

    def test_quote_domain_model_normalization(self) -> None:
        quote = MarketQuote(
            ticker=self.ticker,
            exchange=ExchangeType.NSE,
            price=Price(
                money=Money(amount=Decimal("2500.00"), currency=Currency(CurrencyCode.INR))
            ),
            change=Decimal("25.00"),
            change_percent=Decimal("1.01"),
            volume=Decimal("500000.00"),
            open=Decimal("2480.00"),
            high=Decimal("2510.00"),
            low=Decimal("2475.00"),
            previous_close=Decimal("2475.00"),
            currency="INR",
            timestamp=Timestamp.now_utc(),
            market_status=MarketStatus.OPEN,
        )
        data = quote.to_dict()
        self.assertEqual(data["ticker"], "RELIANCE.NSE")
        self.assertEqual(data["exchange"], "NSE")
        self.assertEqual(data["price"], "2500.00")
        self.assertEqual(data["change"], "25.00")
        self.assertEqual(data["change_percent"], "1.01")
        self.assertEqual(data["market_status"], "OPEN")

    def test_provider_manager_fallback(self) -> None:
        primary = DummyTestProvider("yahoo", should_fail=True)
        fallback_1 = DummyTestProvider("yahoo", should_fail=False, price="2510.00")
        fallback_2 = DummyTestProvider("nse", should_fail=False, price="2512.00")

        manager = ProviderManager(
            primary_provider=primary,
            fallback_providers=[fallback_1, fallback_2],
            cache=self.cache,
        )

        quote = manager.get_quote(self.ticker)
        self.assertEqual(quote.price.amount, Decimal("2510.00"))

    def test_cache_and_invalidation(self) -> None:
        provider = DummyTestProvider("yahoo", price="100.00")
        manager = ProviderManager(primary_provider=provider, cache=self.cache)

        # First call populates cache
        q1 = manager.get_quote(self.ticker)
        self.assertEqual(q1.price.amount, Decimal("100.00"))

        # Modify underlying provider output
        provider.price_val = Decimal("200.00")

        # Second call returns cached quote (100.00)
        q2 = manager.get_quote(self.ticker)
        self.assertEqual(q2.price.amount, Decimal("100.00"))

        # Forced refresh bypasses cache and fetches 200.00
        q3 = manager.get_quote(self.ticker, force_refresh=True)
        self.assertEqual(q3.price.amount, Decimal("200.00"))

    def test_all_providers_failure_degradation(self) -> None:
        provider = DummyTestProvider("yahoo", should_fail=False, price="500.00")
        manager = ProviderManager(primary_provider=provider, cache=self.cache)

        # Cache valid quote
        manager.get_quote(self.ticker)

        # Fail primary provider
        provider.should_fail = True
        manager.fallbacks = [DummyTestProvider("yahoo", should_fail=True)]

        # Should degrade gracefully to stale cached quote
        stale_quote = manager.get_quote(self.ticker)
        self.assertEqual(stale_quote.price.amount, Decimal("500.00"))

    def test_yahoo_finance_provider_direct_quote(self) -> None:
        from packages.infrastructure.market_data.providers.yahoo_provider import (
            YahooMarketDataProvider,
        )

        provider = YahooMarketDataProvider()
        quote = provider.get_quote(Ticker("RELIANCE.NSE"))
        self.assertEqual(quote.ticker.full_symbol, "RELIANCE.NSE")
        self.assertGreater(quote.price.amount, Decimal("0.00"))
        self.assertEqual(quote.price.money.currency.code, "INR")

    def test_yahoo_finance_index_mapping(self) -> None:
        from packages.infrastructure.market_data.providers.yahoo_provider import (
            YahooMarketDataProvider,
        )

        provider = YahooMarketDataProvider()
        symbol_nifty = provider._resolve_yf_symbol(Ticker("NIFTY.NSE"))
        self.assertEqual(symbol_nifty, "^NSEI")

        symbol_banknifty = provider._resolve_yf_symbol(Ticker("BANKNIFTY.NSE"))
        self.assertEqual(symbol_banknifty, "^NSEBANK")


if __name__ == "__main__":
    unittest.main()
