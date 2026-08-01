"""
Fundamental, News, Macro, and Corporate Action Mappers.
"""

from decimal import Decimal
from typing import Any

from packages.domain.enums.market import MarketSegment
from packages.domain.market.company import Company
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.models import (
    CorporateAction,
    FinancialStatementModel,
    MacroDataSeriesModel,
    NewsArticleModel,
)


class FundamentalMapper:
    """Mapper for Company Profile, Balance Sheet, Income Statement, Cash Flow, and Key Metrics."""

    @staticmethod
    def to_company_profile(ticker: Ticker, raw: dict[str, Any]) -> Company:
        name = str(raw.get("name", raw.get("company_name", f"{ticker.symbol} Limited")))
        industry = str(raw.get("industry", "Financial Services"))
        sector_raw = str(raw.get("sector", "LARGE_CAP"))
        try:
            sector_enum = MarketSegment(sector_raw)
        except ValueError:
            sector_enum = MarketSegment.LARGE_CAP

        return Company(
            name=name,
            sector=sector_enum,
            industry=industry,
        )

    @staticmethod
    def to_statement_model(
        ticker: Ticker, statement_type: str, raw: dict[str, Any]
    ) -> FinancialStatementModel:
        period = str(raw.get("period", raw.get("fiscal_period", "FY")))
        year = int(raw.get("fiscal_year", raw.get("year", 2026)))
        metrics = {
            k: v
            for k, v in raw.items()
            if k not in ("period", "fiscal_period", "fiscal_year", "year")
        }
        return FinancialStatementModel(
            ticker=ticker,
            statement_type=statement_type,
            period=period,
            fiscal_year=year,
            metrics=metrics,
        )


class NewsMapper:
    """Mapper for News and Sentiment payloads."""

    @staticmethod
    def to_news_articles(ticker: Ticker, raw_list: list[dict[str, Any]]) -> list[NewsArticleModel]:
        articles: list[NewsArticleModel] = []
        for item in raw_list:
            art = NewsArticleModel(
                ticker=ticker,
                title=str(item.get("title", item.get("headline", ""))),
                content=str(item.get("content", item.get("text", item.get("summary", "")))),
                source=str(item.get("source", item.get("publisher", "MarketNews"))),
                published_at=str(item.get("published_at", item.get("date", "2026-06-01"))),
                url=str(item.get("url", "")),
                sentiment_score=Decimal(
                    str(item.get("sentiment_score", item.get("sentiment", "0.00")))
                ),
            )
            articles.append(art)
        return articles


class MacroMapper:
    """Mapper for Macroeconomic Data Series and Economic Calendar."""

    @staticmethod
    def to_macro_series(
        series_id: str, raw: dict[str, Any] | list[dict[str, Any]]
    ) -> MacroDataSeriesModel:
        if isinstance(raw, list):
            name = f"Macro Series {series_id}"
            unit = "Index"
            data_pts = raw
        else:
            name = str(raw.get("name", f"Macro Series {series_id}"))
            unit = str(raw.get("unit", "Index"))
            data_pts = raw.get("data_points", raw.get("points", []))

        return MacroDataSeriesModel(
            series_id=series_id,
            name=name,
            unit=unit,
            data_points=data_pts,
        )


class CorporateMapper:
    """Mapper for Corporate Actions (Dividends, Splits, Bonus Shares)."""

    @staticmethod
    def to_corporate_actions(
        ticker: Ticker, raw_list: list[dict[str, Any]]
    ) -> list[CorporateAction]:
        actions: list[CorporateAction] = []
        for item in raw_list:
            act = CorporateAction(
                ticker=ticker,
                action_type=str(item.get("action_type", item.get("event", "DIVIDEND"))),
                record_date=str(item.get("record_date", item.get("date", "2026-06-01"))),
                description=str(item.get("description", f"Corporate event: {ticker.symbol}")),
            )
            actions.append(act)
        return actions
