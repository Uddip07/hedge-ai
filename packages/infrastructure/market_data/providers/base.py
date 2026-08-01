"""
Abstract Market Intelligence Provider Interfaces.

Defines standard provider contracts for Quotes, Historical OHLCV, Company Profiles,
Fundamentals, News, Macro, ETFs, Sectors, Exchanges, Economic Calendars, and Corporate Actions.
"""

from abc import ABC, abstractmethod
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


class MarketDataProvider(ABC):
    """
    Abstract Base Class for all Market Intelligence Providers (Yahoo Finance, NSE, etc.).
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier name."""

    @abstractmethod
    def get_quote(self, ticker: Ticker) -> MarketQuote:
        """Fetch current price quote snapshot for a ticker."""

    @abstractmethod
    def get_historical_ohlcv(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> list[Candle]:
        """Fetch historical OHLCV candles."""

    @abstractmethod
    def get_company_profile(self, ticker: Ticker) -> Company:
        """Fetch company corporate profile."""

    @abstractmethod
    def get_market_status(self, exchange: ExchangeType) -> MarketStatusInfo:
        """Fetch exchange session status."""

    @abstractmethod
    def get_corporate_actions(self, ticker: Ticker) -> list[CorporateAction]:
        """Fetch corporate action events for a ticker."""

    @abstractmethod
    def get_income_statement(self, ticker: Ticker) -> FinancialStatementModel:
        """Fetch annual/quarterly income statement."""

    @abstractmethod
    def get_balance_sheet(self, ticker: Ticker) -> FinancialStatementModel:
        """Fetch annual/quarterly balance sheet."""

    @abstractmethod
    def get_cash_flow_statement(self, ticker: Ticker) -> FinancialStatementModel:
        """Fetch annual/quarterly cash flow statement."""

    @abstractmethod
    def get_news(self, ticker: Ticker) -> list[NewsArticleModel]:
        """Fetch market news and sentiment articles for a ticker."""

    @abstractmethod
    def get_macro_series(self, series_id: str) -> MacroDataSeriesModel:
        """Fetch macroeconomic indicator data series."""

    @abstractmethod
    def get_economic_calendar(self, country: str = "IN") -> list[dict[str, Any]]:
        """Fetch upcoming macroeconomic events and announcements."""

    @abstractmethod
    def get_etf_info(self, ticker: Ticker) -> ETFInfoModel:
        """Fetch ETF metadata, NAV, and holdings."""

    @abstractmethod
    def get_sector_performance(self) -> dict[str, Any]:
        """Fetch sector performance metrics."""

    @abstractmethod
    def get_exchange_metadata(self, exchange: ExchangeType) -> dict[str, Any]:
        """Fetch venue metadata for an exchange."""
