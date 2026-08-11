"""
ProviderManager for Production Market Data Pipelines.

Manages primary (Yahoo Finance) and secondary (NSE/BSE) providers,
automatic fallback execution, TTL caching (3-second market hours TTL, 300-second off-market TTL),
cache invalidation, market status detection, and telemetry.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Any, cast

from packages.domain.enums.market import ExchangeType, MarketSession, MarketStatus, Timeframe
from packages.domain.market.calendar import MarketHoliday, TradingCalendar, TradingSession
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.market.provider import MarketProvider
from packages.domain.market.quote import MarketQuote
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.cache import MarketDataCache
from packages.infrastructure.market_data.models import FinancialStatementModel, NewsArticleModel
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import MarketDataTelemetry, TelemetryTimer

logger = logging.getLogger("ihf_ai.infrastructure.market_data.provider_manager")


class ProviderManager(MarketProvider):
    """
    Production ProviderManager with automatic failover, market status detection,
    and adaptive TTL caching.
    """

    def __init__(
        self,
        primary_provider: Any = None,
        fallback_providers: list[Any] | None = None,
        cache: MarketDataCache | None = None,
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
        calendar: TradingCalendar | None = None,
    ) -> None:
        from packages.infrastructure.market_data.providers.nse_provider import (
            NSEMarketDataProvider,
        )
        from packages.infrastructure.market_data.providers.yahoo_provider import (
            YahooMarketDataProvider,
        )

        self.primary: Any = primary_provider or YahooMarketDataProvider()
        self.fallbacks: list[Any] = (
            fallback_providers if fallback_providers is not None else [NSEMarketDataProvider()]
        )

        self.cache = cache or MarketDataCache()
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

        # Wire trading calendar for NSE/BSE
        self.calendar = calendar or TradingCalendar(
            exchange=ExchangeType.NSE,
            holidays=[
                MarketHoliday(
                    holiday_date=date.fromisoformat("2026-01-26"),
                    description="Republic Day",
                    is_trading_closed=True,
                ),
                MarketHoliday(
                    holiday_date=date.fromisoformat("2026-08-15"),
                    description="Independence Day",
                    is_trading_closed=True,
                ),
                MarketHoliday(
                    holiday_date=date.fromisoformat("2026-10-02"),
                    description="Mahatma Gandhi Jayanti",
                    is_trading_closed=True,
                ),
            ],
            sessions=[
                TradingSession(
                    session_type=MarketSession.PRE_MARKET,
                    start_time=Timestamp.from_iso("2026-01-01T09:00:00+05:30"),
                    end_time=Timestamp.from_iso("2026-01-01T09:15:00+05:30"),
                ),
                TradingSession(
                    session_type=MarketSession.NORMAL,
                    start_time=Timestamp.from_iso("2026-01-01T09:15:00+05:30"),
                    end_time=Timestamp.from_iso("2026-01-01T15:30:00+05:30"),
                ),
                TradingSession(
                    session_type=MarketSession.POST_MARKET,
                    start_time=Timestamp.from_iso("2026-01-01T15:30:00+05:30"),
                    end_time=Timestamp.from_iso("2026-01-01T16:00:00+05:30"),
                ),
            ],
        )

    @property
    def provider_name(self) -> str:
        return "provider_manager"

    def get_market_status(self, exchange: ExchangeType) -> MarketStatus:
        """Detect actual real-time market status using trading calendar & current UTC timestamp."""
        now = Timestamp.now_utc()
        # Ensure session dates dynamically match current date
        now_dt = now.value
        iso_date = now_dt.date().isoformat()

        # Build daily session windows dynamically for target date in IST (+05:30)
        daily_calendar = TradingCalendar(
            exchange=exchange,
            holidays=self.calendar.holidays,
            sessions=[
                TradingSession(
                    session_type=MarketSession.PRE_MARKET,
                    start_time=Timestamp.from_iso(f"{iso_date}T09:00:00+05:30"),
                    end_time=Timestamp.from_iso(f"{iso_date}T09:15:00+05:30"),
                ),
                TradingSession(
                    session_type=MarketSession.NORMAL,
                    start_time=Timestamp.from_iso(f"{iso_date}T09:15:00+05:30"),
                    end_time=Timestamp.from_iso(f"{iso_date}T15:30:00+05:30"),
                ),
                TradingSession(
                    session_type=MarketSession.POST_MARKET,
                    start_time=Timestamp.from_iso(f"{iso_date}T15:30:00+05:30"),
                    end_time=Timestamp.from_iso(f"{iso_date}T16:00:00+05:30"),
                ),
            ],
        )
        return daily_calendar.get_market_status(now)

    def get_cache_ttl(self, exchange: ExchangeType) -> int:
        """
        Return adaptive TTL in seconds:
        3 seconds during OPEN market hours, 30 seconds after close or on holidays.
        """
        status = self.get_market_status(exchange)
        return 3 if status == MarketStatus.OPEN else 30

    def get_quote(
        self, ticker: Ticker, force_refresh: bool = False, provider_override: str | None = None
    ) -> MarketQuote:
        """
        Fetch market quote with caching, provider fallback, and market status injection.
        """
        exch = ticker.exchange or ExchangeType.NSE
        if force_refresh:
            self.cache.invalidate_quote(ticker)
        else:
            cached = self.cache.get_quote(ticker)
            if cached and isinstance(cached, MarketQuote):
                self.telemetry.record_event(
                    provider="cache",
                    operation="get_quote",
                    ticker=ticker.full_symbol,
                    latency_ms=0.1,
                    cache_hit=True,
                    success=True,
                )
                return cached

        providers_to_try: list[MarketProvider] = []
        if provider_override:
            for p in [self.primary] + self.fallbacks:
                if p.provider_name.lower() == provider_override.lower():
                    providers_to_try.append(p)
                    break
        if not providers_to_try:
            providers_to_try = [self.primary] + self.fallbacks

        last_err: Exception | None = None

        for provider in providers_to_try:
            with TelemetryTimer() as timer:
                try:

                    def _fetch_quote(p: Any = provider) -> MarketQuote:
                        res = p.get_quote(ticker)
                        return cast(MarketQuote, res)

                    raw_quote = self.retry_policy.execute(_fetch_quote)
                    real_status = self.get_market_status(exch)

                    # Normalize into final domain MarketQuote with real market status
                    source_val = getattr(raw_quote, "source", "YAHOO")
                    yahoo_sym = getattr(raw_quote, "yahoo_symbol", "")
                    final_quote = MarketQuote(
                        ticker=raw_quote.ticker if hasattr(raw_quote, "ticker") else ticker,
                        exchange=exch,
                        price=raw_quote.price,
                        change=getattr(raw_quote, "change", Decimal("0.00")),
                        change_percent=getattr(raw_quote, "change_percent", Decimal("0.00")),
                        volume=getattr(raw_quote, "volume", Decimal("0.00")),
                        open=getattr(raw_quote, "open", Decimal("0.00")),
                        high=getattr(raw_quote, "high", Decimal("0.00")),
                        low=getattr(raw_quote, "low", Decimal("0.00")),
                        previous_close=getattr(raw_quote, "previous_close", Decimal("0.00")),
                        currency=raw_quote.price.money.currency.code,
                        timestamp=raw_quote.timestamp
                        if (hasattr(raw_quote, "timestamp") and raw_quote.timestamp)
                        else Timestamp.now_utc(),
                        market_status=real_status,
                        source=source_val,
                        yahoo_symbol=yahoo_sym,
                    )

                    ttl = self.get_cache_ttl(exch)
                    self.cache.set_quote(ticker, final_quote, ttl_seconds=ttl)

                    self.telemetry.record_event(
                        provider=provider.provider_name,
                        operation="get_quote",
                        ticker=ticker.full_symbol,
                        latency_ms=timer.latency_ms,
                        cache_hit=False,
                        success=True,
                    )
                    return final_quote
                except Exception as err:
                    logger.warning(
                        "Market quote retrieval failed on provider '%s' for '%s': %s",
                        provider.provider_name,
                        ticker.full_symbol,
                        err,
                    )
                    self.telemetry.record_event(
                        provider=provider.provider_name,
                        operation="get_quote",
                        ticker=ticker.full_symbol,
                        latency_ms=timer.latency_ms,
                        cache_hit=False,
                        success=False,
                        failure_reason=str(err),
                    )
                    last_err = err

        # Fallback to stale cached data if all providers fail
        stale = self.cache.get_quote(ticker)
        if stale and isinstance(stale, MarketQuote):
            logger.error(
                "All market providers failed for '%s'. Serving stale cached quote.",
                ticker.full_symbol,
            )
            return stale

        raise RuntimeError(
            f"All market data providers failed for ticker '{ticker.full_symbol}'. Last error: {last_err}"
        ) from last_err

    def get_historical_candles(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> list[Candle]:
        providers_to_try = [self.primary] + self.fallbacks
        last_err: Exception | None = None

        for provider in providers_to_try:
            try:
                # YahooMarketDataProvider exposes get_historical_ohlcv();
                # future providers may expose get_historical_candles() — support both.
                if hasattr(provider, "get_historical_ohlcv"):
                    res = provider.get_historical_ohlcv(ticker, timeframe, start_time, end_time)
                elif hasattr(provider, "get_historical_candles"):
                    res = provider.get_historical_candles(ticker, timeframe, start_time, end_time)
                else:
                    continue
                if isinstance(res, list):
                    return res
            except Exception as err:
                logger.warning(
                    "Historical OHLCV failed on provider '%s' for '%s': %s",
                    provider.provider_name,
                    ticker.full_symbol,
                    err,
                )
                last_err = err

        return []

    def get_company_profile(self, ticker: Ticker) -> Company | None:
        providers_to_try = [self.primary] + self.fallbacks
        for provider in providers_to_try:
            try:
                res = provider.get_company_profile(ticker)
                if isinstance(res, Company):
                    return res
            except Exception as err:
                logger.warning(
                    "Company profile failed on provider '%s' for '%s': %s",
                    provider.provider_name,
                    ticker.full_symbol,
                    err,
                )
        return None

    def get_income_statement(self, ticker: Ticker) -> FinancialStatementModel | None:
        providers_to_try = [self.primary] + self.fallbacks
        for provider in providers_to_try:
            try:
                res = provider.get_income_statement(ticker)
                if isinstance(res, FinancialStatementModel):
                    return res
            except Exception:
                pass
        return None

    def get_balance_sheet(self, ticker: Ticker) -> FinancialStatementModel | None:
        providers_to_try = [self.primary] + self.fallbacks
        for provider in providers_to_try:
            try:
                res = provider.get_balance_sheet(ticker)
                if isinstance(res, FinancialStatementModel):
                    return res
            except Exception:
                pass
        return None

    def get_cash_flow_statement(self, ticker: Ticker) -> FinancialStatementModel | None:
        providers_to_try = [self.primary] + self.fallbacks
        for provider in providers_to_try:
            try:
                res = provider.get_cash_flow_statement(ticker)
                if isinstance(res, FinancialStatementModel):
                    return res
            except Exception:
                pass
        return None

    def get_news(self, ticker: Ticker) -> list[NewsArticleModel]:
        providers_to_try = [self.primary] + self.fallbacks
        for provider in providers_to_try:
            try:
                res = provider.get_news(ticker)
                if isinstance(res, list) and len(res) > 0:
                    return res
            except Exception:
                pass
        return []
