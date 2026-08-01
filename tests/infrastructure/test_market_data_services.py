"""
Unit tests for Market Data Infrastructure Services across all 11 categories:
QuoteService, HistoricalService, FundamentalService, CompanyProfileService,
CorporateActionService, NewsService, MacroService, EconomicCalendarService,
ETFService, SectorService, ExchangeService.
"""

import unittest
from decimal import Decimal

from packages.domain.enums.market import ExchangeType, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.models import (
    ETFInfoModel,
    FinancialStatementModel,
    MacroDataSeriesModel,
    MarketQuote,
    MarketStatusInfo,
    NewsArticleModel,
)
from packages.infrastructure.market_data.providers.yahoo_provider import (
    YahooMarketDataProvider,
)
from packages.infrastructure.market_data.registries.quote_registry import (
    CorporateActionProviderRegistry,
    ETFProviderRegistry,
    FundamentalProviderRegistry,
    MacroProviderRegistry,
    NewsProviderRegistry,
    QuoteProviderRegistry,
)
from packages.infrastructure.market_data.services.company_profile_service import (
    CompanyProfileService,
)
from packages.infrastructure.market_data.services.corporate_service import (
    CorporateActionService,
)
from packages.infrastructure.market_data.services.economic_calendar_service import (
    EconomicCalendarService,
)
from packages.infrastructure.market_data.services.etf_service import ETFService
from packages.infrastructure.market_data.services.exchange_service import (
    ExchangeService,
)
from packages.infrastructure.market_data.services.fundamental_service import (
    FundamentalService,
)
from packages.infrastructure.market_data.services.historical_service import (
    HistoricalService,
)
from packages.infrastructure.market_data.services.macro_service import MacroService
from packages.infrastructure.market_data.services.news_service import NewsService
from packages.infrastructure.market_data.services.quote_service import QuoteService
from packages.infrastructure.market_data.services.sector_service import SectorService


class TestMarketDataServices(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = YahooMarketDataProvider()
        self.ticker = Ticker("RELIANCE.NSE")

        self.quote_registry = QuoteProviderRegistry()
        self.quote_registry.register("yahoo", self.provider)

        self.fundamental_registry = FundamentalProviderRegistry()
        self.fundamental_registry.register("yahoo", self.provider)

        self.news_registry = NewsProviderRegistry()
        self.news_registry.register("yahoo", self.provider)

        self.macro_registry = MacroProviderRegistry()
        self.macro_registry.register("yahoo", self.provider)

        self.corporate_registry = CorporateActionProviderRegistry()
        self.corporate_registry.register("yahoo", self.provider)

        self.etf_registry = ETFProviderRegistry()
        self.etf_registry.register("yahoo", self.provider)

    def test_quote_service(self) -> None:
        service = QuoteService(registry=self.quote_registry, default_provider="yahoo")
        quote = service.get_quote(self.ticker)
        self.assertIsInstance(quote, MarketQuote)
        self.assertGreater(quote.price.amount, Decimal("0.00"))

    def test_historical_service(self) -> None:
        service = HistoricalService(registry=self.quote_registry, default_provider="yahoo")
        now = Timestamp.now_utc()
        candles = service.get_historical_candles(self.ticker, Timeframe.DAY_1, now, now)
        self.assertIsInstance(candles, list)
        if candles:
            self.assertIsInstance(candles[0], Candle)

    def test_fundamental_service(self) -> None:
        service = FundamentalService(registry=self.fundamental_registry, default_provider="yahoo")
        inc = service.get_income_statement(self.ticker)
        bal = service.get_balance_sheet(self.ticker)
        cash = service.get_cash_flow_statement(self.ticker)
        self.assertIsInstance(inc, FinancialStatementModel)
        self.assertIsInstance(bal, FinancialStatementModel)
        self.assertIsInstance(cash, FinancialStatementModel)

    def test_company_profile_service(self) -> None:
        service = CompanyProfileService(
            registry=self.fundamental_registry, default_provider="yahoo"
        )
        profile = service.get_company_profile(self.ticker)
        self.assertIsInstance(profile, Company)
        self.assertTrue(len(profile.name) > 0)

    def test_corporate_action_service(self) -> None:
        service = CorporateActionService(registry=self.corporate_registry, default_provider="yahoo")
        actions = service.get_corporate_actions(self.ticker)
        self.assertIsInstance(actions, list)

    def test_news_service(self) -> None:
        service = NewsService(registry=self.news_registry, default_provider="yahoo")
        news = service.get_news(self.ticker)
        self.assertIsInstance(news, list)
        if news:
            self.assertIsInstance(news[0], NewsArticleModel)

    def test_macro_service(self) -> None:
        service = MacroService(registry=self.macro_registry, default_provider="yahoo")
        macro = service.get_macro_series("REPO_RATE")
        self.assertIsInstance(macro, MacroDataSeriesModel)

    def test_economic_calendar_service(self) -> None:
        service = EconomicCalendarService(registry=self.macro_registry, default_provider="yahoo")
        cal = service.get_economic_calendar("IN")
        self.assertIsInstance(cal, list)
        self.assertEqual(cal[0]["country"], "IN")

    def test_etf_service(self) -> None:
        service = ETFService(registry=self.etf_registry, default_provider="yahoo")
        etf = service.get_etf_info(self.ticker)
        self.assertIsInstance(etf, ETFInfoModel)
        self.assertEqual(etf.nav, Decimal("250.00"))

    def test_sector_service(self) -> None:
        service = SectorService(registry=self.fundamental_registry, default_provider="yahoo")
        sectors = service.get_sector_performance()
        self.assertIn("IT", sectors)

    def test_exchange_service(self) -> None:
        service = ExchangeService(registry=self.quote_registry, default_provider="yahoo")
        status_info = service.get_market_status(ExchangeType.NSE)
        self.assertIsInstance(status_info, MarketStatusInfo)
        meta = service.get_exchange_metadata(ExchangeType.NSE)
        self.assertEqual(meta["exchange"], "NSE")


if __name__ == "__main__":
    unittest.main()
