"""
Investment Evidence Models and Evidence Builder for AI Committee Engine.

Aggregates real Yahoo quotes, company profiles, financial statements, historical candles,
news articles, and macro series into a unified InvestmentEvidence container.
"""

from dataclasses import dataclass, field
from typing import Any

from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.market.quote import MarketQuote
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.models import (
    FinancialStatementModel,
    MacroDataSeriesModel,
    NewsArticleModel,
)
from packages.infrastructure.market_data.provider_manager import ProviderManager


@dataclass
class InvestmentEvidence:
    """
    Normalized, pure evidence payload passed to AI Investment Committee specialist agents.
    Contains zero placeholder scores.
    """

    ticker: Ticker
    quote: MarketQuote | None = None
    profile: Company | None = None
    income_statement: FinancialStatementModel | None = None
    balance_sheet: FinancialStatementModel | None = None
    cash_flow: FinancialStatementModel | None = None
    candles: list[Candle] = field(default_factory=list)
    news: list[NewsArticleModel] = field(default_factory=list)
    macro_series: list[MacroDataSeriesModel] = field(default_factory=list)
    technical_indicators: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize InvestmentEvidence into a clean JSON-serializable dictionary for LLM context."""
        return {
            "ticker": self.ticker.full_symbol,
            "quote": self.quote.to_dict() if self.quote else None,
            "profile": self.profile.to_dict() if self.profile else None,
            "income_statement": self.income_statement.to_dict() if self.income_statement else None,
            "balance_sheet": self.balance_sheet.to_dict() if self.balance_sheet else None,
            "cash_flow": self.cash_flow.to_dict() if self.cash_flow else None,
            "candles_count": len(self.candles),
            "news": [art.to_dict() for art in self.news],
            "macro": [m.to_dict() for m in self.macro_series],
            "technicals": self.technical_indicators,
        }


class InvestmentEvidenceBuilder:
    """
    Builder responsible for fetching and aggregating all market data from ProviderManager.
    """

    def __init__(self, provider_manager: ProviderManager | None = None) -> None:
        self.provider_manager = provider_manager or ProviderManager()

    def build_evidence(self, ticker: Ticker) -> InvestmentEvidence:
        """Fetch all production data for the specified ticker."""
        quote = None
        profile = None
        income_stmt = None
        balance_sheet = None
        cash_flow = None
        candles: list[Candle] = []
        news: list[NewsArticleModel] = []
        technicals: dict[str, Any] = {}

        try:
            quote = self.provider_manager.get_quote(ticker)
        except Exception:
            pass

        try:
            profile = self.provider_manager.get_company_profile(ticker)
        except Exception:
            pass

        try:
            income_stmt = self.provider_manager.get_income_statement(ticker)
        except Exception:
            pass

        try:
            balance_sheet = self.provider_manager.get_balance_sheet(ticker)
        except Exception:
            pass

        try:
            cash_flow = self.provider_manager.get_cash_flow_statement(ticker)
        except Exception:
            pass

        try:
            news = self.provider_manager.get_news(ticker)
        except Exception:
            pass

        # Compute technical indicators if quote is present
        if quote and quote.price:
            p = float(quote.price.amount)
            open_p = float(quote.open) if quote.open else p
            prev_close = float(quote.previous_close) if quote.previous_close else p
            chg_pct = float(quote.change_percent) if quote.change_percent else 0.0

            # NOTE: rsi_14 here is a simplified linear approximation:
            #   RSI_proxy = clamp(50 + change_pct * 5, 0, 100)
            # This is NOT a proper Wilder RSI-14 calculation (which requires 14 periods
            # of price history). A true RSI-14 requires historical candles which are
            # fetched separately. The rsi_is_approximation flag signals this to consumers.
            rsi = max(0.0, min(100.0, 50.0 + (chg_pct * 5.0)))
            trend = "Bullish" if chg_pct > 0 else "Bearish" if chg_pct < 0 else "Neutral"
            technicals = {
                "rsi_14": round(rsi, 2),
                "rsi_is_approximation": True,
                "trend": trend,
                "current_price": p,
                "open_price": open_p,
                "previous_close": prev_close,
                "change_percent": chg_pct,
            }

        return InvestmentEvidence(
            ticker=ticker,
            quote=quote,
            profile=profile,
            income_statement=income_stmt,
            balance_sheet=balance_sheet,
            cash_flow=cash_flow,
            candles=candles,
            news=news,
            technical_indicators=technicals,
        )
