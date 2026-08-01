"""
Delegating Market Data Provider.

A thin delegation layer that forwards all calls to YahooMarketDataProvider.
This provider is NOT a mock — it is used when a single-provider shim is needed
without the full ProviderManager fallback chain.
"""

from typing import Any

from packages.domain.enums.market import ExchangeType, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.models import (
    CorporateAction,
    ETFInfoModel,
    FinancialStatementModel,
    MacroDataSeriesModel,
    MarketQuote,
    MarketStatusInfo,
    NewsArticleModel,
)
from packages.infrastructure.market_data.providers.base import MarketDataProvider
from packages.infrastructure.market_data.providers.yahoo_provider import (
    YahooMarketDataProvider,
)


class DelegatingMarketDataProvider(MarketDataProvider):
    """
    Delegation shim forwarding all MarketDataProvider calls to YahooMarketDataProvider.

    This is NOT a mock. Use this class when a single provider wrapper is needed
    without the full ProviderManager fallback chain (e.g. isolated unit testing
    with a real Yahoo backend).
    """

    def __init__(self) -> None:
        self._provider = YahooMarketDataProvider()

    @property
    def provider_name(self) -> str:
        return "yahoo_delegating"

    def get_quote(self, ticker: Ticker) -> MarketQuote:
        return self._provider.get_quote(ticker)

    def get_historical_ohlcv(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> list[Candle]:
        return self._provider.get_historical_ohlcv(ticker, timeframe, start_time, end_time)

    def get_company_profile(self, ticker: Ticker) -> Company:
        return self._provider.get_company_profile(ticker)

    def get_market_status(self, exchange: ExchangeType) -> MarketStatusInfo:
        return self._provider.get_market_status(exchange)

    def get_corporate_actions(self, ticker: Ticker) -> list[CorporateAction]:
        return self._provider.get_corporate_actions(ticker)

    def get_income_statement(self, ticker: Ticker) -> FinancialStatementModel:
        return self._provider.get_income_statement(ticker)

    def get_balance_sheet(self, ticker: Ticker) -> FinancialStatementModel:
        return self._provider.get_balance_sheet(ticker)

    def get_cash_flow_statement(self, ticker: Ticker) -> FinancialStatementModel:
        return self._provider.get_cash_flow_statement(ticker)

    def get_news(self, ticker: Ticker) -> list[NewsArticleModel]:
        return self._provider.get_news(ticker)

    def get_macro_series(self, series_id: str) -> MacroDataSeriesModel:
        return self._provider.get_macro_series(series_id)

    def get_economic_calendar(self, country: str = "IN") -> list[dict[str, Any]]:
        return self._provider.get_economic_calendar(country)

    def get_etf_info(self, ticker: Ticker) -> ETFInfoModel:
        return self._provider.get_etf_info(ticker)

    def get_sector_performance(self) -> dict[str, Any]:
        return self._provider.get_sector_performance()

    def get_exchange_metadata(self, exchange: ExchangeType) -> dict[str, Any]:
        return self._provider.get_exchange_metadata(exchange)


# Backward-compatibility alias — prefer DelegatingMarketDataProvider in new code.
MockMarketDataProvider = DelegatingMarketDataProvider
