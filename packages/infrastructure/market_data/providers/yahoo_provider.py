import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from packages.domain.enums.market import ExchangeType, MarketSegment, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.mappers.quote_mapper import QuoteMapper
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
from packages.infrastructure.market_data.validators.quote_validator import QuoteValidator

logger = logging.getLogger("ihf_ai.infrastructure.market_data.yahoo_provider")


class YahooMarketDataProvider(MarketDataProvider):
    INDEX_MAP = {
        "NIFTY": "^NSEI",
        "NIFTY50": "^NSEI",
        "NIFTY 50": "^NSEI",
        "NIFTY.NSE": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "BANKNIFTY.NSE": "^NSEBANK",
        "SENSEX": "^BSESN",
        "SENSEX.BSE": "^BSESN",
    }

    _TIMEFRAME_MAP = {
        Timeframe.MINUTE_1: ("1m", "7d"),
        Timeframe.MINUTE_5: ("5m", "60d"),
        Timeframe.MINUTE_15: ("15m", "60d"),
        Timeframe.HOUR_1: ("60m", "730d"),
        Timeframe.DAY_1: ("1d", "1y"),
        Timeframe.WEEK_1: ("1wk", "5y"),
        Timeframe.MONTH_1: ("1mo", "10y"),
    }

    def __init__(self) -> None:
        self._ticker_cache: dict[str, Any] = {}

    @property
    def provider_name(self) -> str:
        return "yahoo"

    def _resolve_yf_symbol(self, ticker: Ticker) -> str:
        symbol = ticker.symbol.strip().upper()
        full_symbol = ticker.full_symbol.strip().upper()

        # Handle well-known indices
        if symbol in self.INDEX_MAP:
            return self.INDEX_MAP[symbol]

        if full_symbol in self.INDEX_MAP:
            return self.INDEX_MAP[full_symbol]

        # Already a Yahoo symbol
        if symbol.startswith("^"):
            return symbol

        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            return symbol

        # Exchange-specific mapping
        exchange_map = {
            ExchangeType.NSE: ".NS",
            ExchangeType.BSE: ".BO",
        }
        suffix = exchange_map.get(ticker.exchange) if ticker.exchange is not None else None
        if suffix is None:
            logger.warning(
                "Unknown exchange '%s' for ticker '%s'. Falling back to NSE.",
                ticker.exchange,
                ticker.full_symbol,
            )
            suffix = ".NS"
        return f"{symbol}{suffix}"

    def _get_ticker(self, ticker: Ticker) -> Any:
        """
        Returns a cached Yahoo Finance ticker object.
        """

        import yfinance as yf

        symbol = self._resolve_yf_symbol(ticker)

        ticker_obj = self._ticker_cache.get(symbol)

        if ticker_obj is None:
            ticker_obj = yf.Ticker(symbol)
            self._ticker_cache[symbol] = ticker_obj

        return ticker_obj

    @staticmethod
    def _safe_get(obj: Any, attr: str, alt: str | None = None) -> Any:
        """
        Safely retrieve attributes from either dictionaries
        or normal objects.
        """

        if obj is None:
            return None

        if isinstance(obj, dict):
            return obj.get(alt or attr)

        value = getattr(obj, attr, None)

        if value is None and alt:
            value = getattr(obj, alt, None)

        return value

    @staticmethod
    def _to_decimal(value: Any) -> Decimal | None:
        if value is None:
            return None

        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except Exception:
            return None

    @staticmethod
    def _extract_metric(frame: Any, metric: str) -> str | None:
        """
        Safely extracts a metric from a pandas DataFrame.
        """

        if frame is None or frame.empty:
            return None

        if metric not in frame.index:
            return None

        column = frame.columns[0]

        value = frame.loc[metric, column]

        if value is None:
            return None

        return str(value)

    def get_quote(self, ticker: Ticker) -> MarketQuote:
        yf_symbol = self._resolve_yf_symbol(ticker)
        try:
            ticker_obj = self._get_ticker(ticker)
            fast_info = getattr(ticker_obj, "fast_info", {})
            info = getattr(ticker_obj, "info", {})
            last_price = self._safe_get(fast_info, "last_price", "lastPrice") or info.get(
                "regularMarketPrice"
            )
            if last_price is None:
                raise RuntimeError("Yahoo Finance returned no market price.")
            previous_close = self._safe_get(
                fast_info, "previous_close", "previousClose"
            ) or info.get("regularMarketPreviousClose")

            open_price = self._safe_get(fast_info, "open") or info.get("regularMarketOpen")

            high_price = self._safe_get(fast_info, "day_high", "dayHigh") or info.get(
                "regularMarketDayHigh"
            )

            low_price = self._safe_get(fast_info, "day_low", "dayLow") or info.get(
                "regularMarketDayLow"
            )

            volume = self._safe_get(fast_info, "last_volume", "lastVolume") or info.get(
                "regularMarketVolume"
            )

            currency = self._safe_get(fast_info, "currency") or info.get("currency") or "INR"

            last = self._to_decimal(last_price) or Decimal("0")

            previous = self._to_decimal(previous_close) or last
            opening = self._to_decimal(open_price) or last
            high = self._to_decimal(high_price) or last
            low = self._to_decimal(low_price) or last
            volume = self._to_decimal(volume) or Decimal("0")

            change = last - previous

            if previous == Decimal("0"):
                change_percent = Decimal("0")
            else:
                change_percent = (change / previous) * Decimal("100")

            payload = {
                "symbol": ticker.full_symbol,
                "price": str(last),
                "change": str(change.quantize(Decimal("0.01"))),
                "change_percent": str(change_percent.quantize(Decimal("0.01"))),
                "volume": str(volume),
                "open": str(opening),
                "high": str(high),
                "low": str(low),
                "previous_close": str(previous),
                "currency": currency,
                "timestamp": Timestamp.now_utc().isoformat(),
            }

            validated = QuoteValidator.validate_quote(payload)

            return QuoteMapper.to_market_quote(
                ticker,
                validated,
            )

        except Exception as err:
            logger.exception(
                "Yahoo Finance quote retrieval failed for '%s'",
                yf_symbol,
            )
            raise RuntimeError(
                f"Failed to retrieve quote for '{yf_symbol}' from Yahoo Finance."
            ) from err

    def get_historical_ohlcv(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> list[Candle]:
        """
        Fetch historical OHLCV candles from Yahoo Finance.
        """

        yf_symbol = self._resolve_yf_symbol(ticker)
        interval, default_period = self._TIMEFRAME_MAP.get(timeframe, ("1d", "1y"))

        try:
            import yfinance as yf

            # Prefer explicit dates if provided
            if start_time and end_time:
                df = yf.download(
                    yf_symbol,
                    start=start_time.isoformat(),
                    end=end_time.isoformat(),
                    interval=interval,
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )
            else:
                df = yf.download(
                    yf_symbol,
                    period=default_period,
                    interval=interval,
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )

            if df.empty:
                logger.warning(
                    "Yahoo returned no historical data for %s",
                    yf_symbol,
                )
                return []

            raw_candles: list[dict[str, Any]] = []

            for timestamp, row in df.iterrows():

                def value(column: str, row: Any = row) -> Any:
                    cell = row[column]
                    return cell.iloc[0] if hasattr(cell, "iloc") else cell

                raw_candles.append(
                    {
                        "date": timestamp.isoformat(),
                        "open": str(value("Open")),
                        "high": str(value("High")),
                        "low": str(value("Low")),
                        "close": str(value("Close")),
                        "volume": int(value("Volume")),
                    }
                )

            validated = QuoteValidator.validate_candles(raw_candles)

            return QuoteMapper.to_candles(
                ticker,
                timeframe,
                validated,
            )

        except Exception as exc:
            logger.exception(
                "Failed retrieving historical data for '%s': %s",
                yf_symbol,
                exc,
            )
            return []

    def get_company_profile(self, ticker: Ticker) -> Company:
        yf_symbol = self._resolve_yf_symbol(ticker)
        try:
            ticker_obj = self._get_ticker(ticker)
            info = getattr(ticker_obj, "info", {}) or {}

            company_name = info.get("longName") or info.get("shortName") or ticker.symbol

            industry = info.get("industry") or info.get("sector") or "Unknown"

            sector_text = (info.get("sector") or "").upper().replace(" ", "_")

            try:
                sector = MarketSegment(sector_text)
            except Exception:
                sector = MarketSegment.LARGE_CAP

            return Company(
                name=company_name,
                sector=sector,
                industry=industry,
                market_cap=self._safe_float(info.get("marketCap")),
                enterprise_value=self._safe_float(info.get("enterpriseValue")),
                employees=self._safe_int(info.get("fullTimeEmployees")),
                country=info.get("country"),
                currency=info.get("currency"),
                website=info.get("website"),
                long_business_summary=info.get("longBusinessSummary"),
                beta=self._safe_float(info.get("beta")),
                trailing_pe=self._safe_float(info.get("trailingPE")),
                forward_pe=self._safe_float(info.get("forwardPE")),
                book_value=self._safe_float(info.get("bookValue")),
                price_to_book=self._safe_float(info.get("priceToBook")),
                dividend_yield=self._safe_float(info.get("dividendYield")),
                fifty_two_week_high=self._safe_float(info.get("fiftyTwoWeekHigh")),
                fifty_two_week_low=self._safe_float(info.get("fiftyTwoWeekLow")),
                average_volume=self._safe_float(info.get("averageVolume")),
                shares_outstanding=self._safe_float(info.get("sharesOutstanding")),
            )

        except Exception as exc:
            logger.exception(
                "Failed retrieving company profile for '%s': %s",
                yf_symbol,
                exc,
            )

            return Company(
                name=ticker.symbol,
                sector=MarketSegment.LARGE_CAP,
                industry="Unknown",
                market_cap=None,
                enterprise_value=None,
                employees=None,
                country=None,
                currency=None,
                website=None,
                long_business_summary=None,
                beta=None,
                trailing_pe=None,
                forward_pe=None,
                book_value=None,
                price_to_book=None,
                dividend_yield=None,
                fifty_two_week_high=None,
                fifty_two_week_low=None,
                average_volume=None,
                shares_outstanding=None,
            )

    def get_market_status(self, exchange: ExchangeType) -> MarketStatusInfo:

        return MarketStatusInfo(
            exchange=exchange,
            is_open=False,
            session="UNKNOWN",
        )

    def get_corporate_actions(self, ticker: Ticker) -> list[CorporateAction]:
        """
        Fetch dividends and stock splits from Yahoo Finance.
        """

        try:
            ticker_obj = self._get_ticker(ticker)

            actions = getattr(ticker_obj, "actions", None)

            if actions is None or actions.empty:
                return []

            corporate_actions: list[CorporateAction] = []

            for timestamp, row in actions.iterrows():
                dividend = row.get("Dividends", 0)
                split = row.get("Stock Splits", 0)

                if dividend:
                    corporate_actions.append(
                        CorporateAction(
                            ticker=ticker,
                            action_type="DIVIDEND",
                            record_date=timestamp.isoformat(),
                            description="Dividend",
                        )
                    )

                if split:
                    corporate_actions.append(
                        CorporateAction(
                            ticker=ticker,
                            action_type="SPLIT",
                            record_date=timestamp.isoformat(),
                            description="Stock split",
                        )
                    )

            return corporate_actions

        except Exception:
            logger.exception(
                "Failed retrieving corporate actions for %s",
                ticker.full_symbol,
            )
            return []

    def get_macro_series(self, series_id: str) -> MacroDataSeriesModel:
        """
        Yahoo Finance is not a macroeconomic data provider.
        """

        return MacroDataSeriesModel(
            series_id=series_id,
            name=series_id,
            unit="UNKNOWN",
            data_points=[],
        )

    def get_economic_calendar(self, country: str = "IN") -> list[dict[str, Any]]:
        """
        Not supported by Yahoo Finance.

        Future provider:
            TradingEconomics
            RBI
            FRED
        """

        return []

    def get_etf_info(self, ticker: Ticker) -> ETFInfoModel:
        """
        Fetch ETF metadata from Yahoo Finance.
        """

        try:
            info = self._get_ticker(ticker).info

            return ETFInfoModel(
                ticker=ticker,
                name=info.get("longName") or ticker.symbol,
                category=str(info.get("category") or ""),
                nav=self._to_decimal(info.get("navPrice")) or Decimal("0.00"),
                aum=self._to_decimal(info.get("totalAssets")) or Decimal("0.00"),
                holdings=[],
            )

        except Exception:
            logger.exception(
                "Failed retrieving ETF information for %s",
                ticker.full_symbol,
            )

            return ETFInfoModel(
                ticker=ticker,
                name=ticker.symbol,
                category="",
                nav=Decimal("0.00"),
                aum=Decimal("0.00"),
                holdings=[],
            )

    def get_sector_performance(self) -> dict[str, Any]:
        """
        Will later be computed from live sector constituents.

        Returning fake percentages is worse than returning nothing.
        """

        return {}

    def get_exchange_metadata(self, exchange: ExchangeType) -> dict[str, Any]:

        metadata = {
            ExchangeType.NSE: {
                "exchange": "NSE",
                "timezone": "Asia/Kolkata",
                "currency": "INR",
                "country": "India",
            },
            ExchangeType.BSE: {
                "exchange": "BSE",
                "timezone": "Asia/Kolkata",
                "currency": "INR",
                "country": "India",
            },
        }

        return metadata.get(
            exchange,
            {
                "exchange": exchange.value,
                "timezone": None,
                "currency": None,
                "country": None,
            },
        )

    def get_income_statement(
        self,
        ticker: Ticker,
    ) -> FinancialStatementModel:
        """
        Fetch the latest annual income statement from Yahoo Finance.
        """

        yf_symbol = self._resolve_yf_symbol(ticker)

        try:
            ticker_obj = self._get_ticker(ticker)

            financials = getattr(ticker_obj, "financials", None)

            if financials is None or financials.empty:
                logger.warning(
                    "Yahoo returned no income statement for %s",
                    yf_symbol,
                )

                return FinancialStatementModel(
                    ticker=ticker,
                    statement_type="INCOME_STATEMENT",
                    period="ANNUAL",
                    fiscal_year=None,
                    metrics={},
                )

            latest_period = financials.columns[0]

            fiscal_year = latest_period.year if hasattr(latest_period, "year") else None

            metrics = {
                "Revenue": self._extract_metric(
                    financials,
                    "Total Revenue",
                ),
                "Cost of Revenue": self._extract_metric(
                    financials,
                    "Cost Of Revenue",
                ),
                "Gross Profit": self._extract_metric(
                    financials,
                    "Gross Profit",
                ),
                "Operating Income": self._extract_metric(
                    financials,
                    "Operating Income",
                ),
                "Net Income": self._extract_metric(
                    financials,
                    "Net Income",
                ),
                "EBIT": self._extract_metric(
                    financials,
                    "EBIT",
                ),
                "EBITDA": self._extract_metric(
                    financials,
                    "EBITDA",
                ),
                "EPS": self._extract_metric(
                    financials,
                    "Basic EPS",
                ),
                "Interest Expense": self._extract_metric(
                    financials,
                    "Interest Expense",
                ),
                "Tax Expense": self._extract_metric(
                    financials,
                    "Tax Provision",
                ),
            }

            metrics = {key: value for key, value in metrics.items() if value is not None}

            return FinancialStatementModel(
                ticker=ticker,
                statement_type="INCOME_STATEMENT",
                period="ANNUAL",
                fiscal_year=fiscal_year,
                metrics=metrics,
            )

        except Exception as exc:
            logger.exception(
                "Failed retrieving income statement for %s: %s",
                yf_symbol,
                exc,
            )

            return FinancialStatementModel(
                ticker=ticker,
                statement_type="INCOME_STATEMENT",
                period="ANNUAL",
                fiscal_year=None,
                metrics={},
            )

    def get_balance_sheet(
        self,
        ticker: Ticker,
    ) -> FinancialStatementModel:
        """
        Fetch the latest annual balance sheet from Yahoo Finance.
        """

        yf_symbol = self._resolve_yf_symbol(ticker)

        try:
            ticker_obj = self._get_ticker(ticker)

            balance_sheet = getattr(ticker_obj, "balance_sheet", None)

            if balance_sheet is None or balance_sheet.empty:
                logger.warning(
                    "Yahoo returned no balance sheet for %s",
                    yf_symbol,
                )

                return FinancialStatementModel(
                    ticker=ticker,
                    statement_type="BALANCE_SHEET",
                    period="ANNUAL",
                    fiscal_year=None,
                    metrics={},
                )

            latest_period = balance_sheet.columns[0]

            fiscal_year = latest_period.year if hasattr(latest_period, "year") else None

            metrics = {
                "Cash": self._extract_metric(
                    balance_sheet,
                    "Cash And Cash Equivalents",
                ),
                "Current Assets": self._extract_metric(
                    balance_sheet,
                    "Current Assets",
                ),
                "Total Assets": self._extract_metric(
                    balance_sheet,
                    "Total Assets",
                ),
                "Current Liabilities": self._extract_metric(
                    balance_sheet,
                    "Current Liabilities",
                ),
                "Total Liabilities": self._extract_metric(
                    balance_sheet,
                    "Total Liabilities Net Minority Interest",
                ),
                "Shareholder Equity": self._extract_metric(
                    balance_sheet,
                    "Stockholders Equity",
                ),
                "Debt": self._extract_metric(
                    balance_sheet,
                    "Total Debt",
                ),
                "Working Capital": self._extract_metric(
                    balance_sheet,
                    "Working Capital",
                ),
                "Inventory": self._extract_metric(
                    balance_sheet,
                    "Inventory",
                ),
                "Accounts Receivable": self._extract_metric(
                    balance_sheet,
                    "Accounts Receivable",
                ),
            }

            metrics = {key: value for key, value in metrics.items() if value is not None}

            return FinancialStatementModel(
                ticker=ticker,
                statement_type="BALANCE_SHEET",
                period="ANNUAL",
                fiscal_year=fiscal_year,
                metrics=metrics,
            )

        except Exception as exc:
            logger.exception(
                "Failed retrieving balance sheet for %s: %s",
                yf_symbol,
                exc,
            )

            return FinancialStatementModel(
                ticker=ticker,
                statement_type="BALANCE_SHEET",
                period="ANNUAL",
                fiscal_year=None,
                metrics={},
            )

    def get_cash_flow_statement(
        self,
        ticker: Ticker,
    ) -> FinancialStatementModel:
        """
        Fetch the latest annual cash flow statement from Yahoo Finance.
        """

        yf_symbol = self._resolve_yf_symbol(ticker)

        try:
            ticker_obj = self._get_ticker(ticker)

            cashflow = getattr(ticker_obj, "cashflow", None)

            if cashflow is None or cashflow.empty:
                logger.warning(
                    "Yahoo returned no cash flow statement for %s",
                    yf_symbol,
                )

                return FinancialStatementModel(
                    ticker=ticker,
                    statement_type="CASH_FLOW",
                    period="ANNUAL",
                    fiscal_year=None,
                    metrics={},
                )

            latest_period = cashflow.columns[0]

            fiscal_year = latest_period.year if hasattr(latest_period, "year") else None

            metrics = {
                "Operating Cash Flow": self._extract_metric(
                    cashflow,
                    "Operating Cash Flow",
                ),
                "Investing Cash Flow": self._extract_metric(
                    cashflow,
                    "Investing Cash Flow",
                ),
                "Financing Cash Flow": self._extract_metric(
                    cashflow,
                    "Financing Cash Flow",
                ),
                "Free Cash Flow": self._extract_metric(
                    cashflow,
                    "Free Cash Flow",
                ),
                "Capital Expenditure": self._extract_metric(
                    cashflow,
                    "Capital Expenditure",
                ),
                "Depreciation": self._extract_metric(
                    cashflow,
                    "Depreciation",
                ),
                "Net Borrowings": self._extract_metric(
                    cashflow,
                    "Net Borrowings",
                ),
            }

            metrics = {key: value for key, value in metrics.items() if value is not None}

            return FinancialStatementModel(
                ticker=ticker,
                statement_type="CASH_FLOW",
                period="ANNUAL",
                fiscal_year=fiscal_year,
                metrics=metrics,
            )

        except Exception as exc:
            logger.exception(
                "Failed retrieving cash flow statement for %s: %s",
                yf_symbol,
                exc,
            )

            return FinancialStatementModel(
                ticker=ticker,
                statement_type="CASH_FLOW",
                period="ANNUAL",
                fiscal_year=None,
                metrics={},
            )

    def get_news(
        self,
        ticker: Ticker,
    ) -> list[NewsArticleModel]:
        """
        Fetch recent Yahoo Finance news.
        """

        yf_symbol = self._resolve_yf_symbol(ticker)

        try:
            ticker_obj = self._get_ticker(ticker)

            raw_news = getattr(ticker_obj, "news", []) or []

            articles: list[NewsArticleModel] = []
            seen_titles: set[str] = set()

            for item in raw_news:
                title = (item.get("title") or item.get("headline") or "").strip()

                if not title:
                    continue

                if title in seen_titles:
                    continue

                seen_titles.add(title)

                publisher = item.get("publisher") or item.get("source") or "Yahoo Finance"

                publish_time = item.get("providerPublishTime")

                if publish_time:
                    published_at = datetime.fromtimestamp(
                        publish_time,
                        tz=UTC,
                    ).isoformat()
                else:
                    published_at = Timestamp.now_utc().isoformat()

                url = item.get("link") or item.get("url") or ""

                summary = item.get("summary") or title

                articles.append(
                    NewsArticleModel(
                        ticker=ticker,
                        title=title,
                        content=summary,
                        source=publisher,
                        published_at=published_at,
                        url=url,
                        # Replace with FinBERT later
                        sentiment_score=None,
                    )
                )

            return articles

        except Exception as exc:
            logger.exception(
                "Failed retrieving Yahoo news for %s: %s",
                yf_symbol,
                exc,
            )

            return []
