"""
Analysis Value Objects for the Indian AI Hedge Fund Domain.

Provides FundamentalAnalysis, TechnicalAnalysis, MacroAnalysis, and SentimentAnalysis models.
Pure domain value objects with zero infrastructure dependencies.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.enums.strategy import SignalType
from packages.domain.value_objects.core.percentage import Percentage
from packages.domain.value_objects.metrics.indicators import ATR, MACD, RSI
from packages.domain.value_objects.metrics.scores import ConfidenceScore


@dataclass(frozen=True, slots=True)
class FundamentalAnalysis:
    """
    Immutable value object for fundamental financial ratios and company valuation metrics.

    Attributes:
        pe_ratio (Optional[Decimal]): Price to Earnings ratio.
        pb_ratio (Optional[Decimal]): Price to Book ratio.
        roe_pct (Optional[Percentage]): Return on Equity percentage.
        roce_pct (Optional[Percentage]): Return on Capital Employed percentage.
        eps (Optional[Decimal]): Earnings Per Share.
        dividend_yield_pct (Optional[Percentage]): Dividend Yield percentage.
        summary (str): Analyst or LLM summary of fundamental thesis.
    """

    pe_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    roe_pct: Percentage | None = None
    roce_pct: Percentage | None = None
    eps: Decimal | None = None
    dividend_yield_pct: Percentage | None = None
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize FundamentalAnalysis to dictionary."""
        return {
            "pe_ratio": str(self.pe_ratio) if self.pe_ratio is not None else None,
            "pb_ratio": str(self.pb_ratio) if self.pb_ratio is not None else None,
            "roe_pct": self.roe_pct.to_dict() if self.roe_pct else None,
            "roce_pct": self.roce_pct.to_dict() if self.roce_pct else None,
            "eps": str(self.eps) if self.eps is not None else None,
            "dividend_yield_pct": (
                self.dividend_yield_pct.to_dict() if self.dividend_yield_pct else None
            ),
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FundamentalAnalysis":
        """Deserialize dictionary to FundamentalAnalysis."""
        return cls(
            pe_ratio=Decimal(str(data["pe_ratio"])) if data.get("pe_ratio") else None,
            pb_ratio=Decimal(str(data["pb_ratio"])) if data.get("pb_ratio") else None,
            roe_pct=Percentage.from_dict(data["roe_pct"]) if data.get("roe_pct") else None,
            roce_pct=Percentage.from_dict(data["roce_pct"]) if data.get("roce_pct") else None,
            eps=Decimal(str(data["eps"])) if data.get("eps") else None,
            dividend_yield_pct=(
                Percentage.from_dict(data["dividend_yield_pct"])
                if data.get("dividend_yield_pct")
                else None
            ),
            summary=data.get("summary", ""),
        )


@dataclass(frozen=True, slots=True)
class TechnicalAnalysis:
    """
    Immutable value object for technical indicators and price action analysis.

    Attributes:
        rsi (Optional[RSI]): Relative Strength Index value object.
        macd (Optional[MACD]): MACD indicator value object.
        atr (Optional[ATR]): Average True Range volatility indicator.
        trend_signal (Optional[SignalType]): Trend direction signal (BUY/SELL/HOLD).
        summary (str): Technical analysis summary text.
    """

    rsi: RSI | None = None
    macd: MACD | None = None
    atr: ATR | None = None
    trend_signal: SignalType | None = None
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize TechnicalAnalysis to dictionary."""
        return {
            "rsi": self.rsi.to_dict() if self.rsi else None,
            "macd": self.macd.to_dict() if self.macd else None,
            "atr": self.atr.to_dict() if self.atr else None,
            "trend_signal": self.trend_signal.value if self.trend_signal else None,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TechnicalAnalysis":
        """Deserialize dictionary to TechnicalAnalysis."""
        return cls(
            rsi=RSI.from_dict(data["rsi"]) if data.get("rsi") else None,
            macd=MACD.from_dict(data["macd"]) if data.get("macd") else None,
            atr=ATR.from_dict(data["atr"]) if data.get("atr") else None,
            trend_signal=SignalType(data["trend_signal"]) if data.get("trend_signal") else None,
            summary=data.get("summary", ""),
        )


@dataclass(frozen=True, slots=True)
class MacroAnalysis:
    """
    Immutable value object for macroeconomic environment evaluation (RBI interest rates, inflation).

    Attributes:
        interest_rate_pct (Optional[Percentage]): RBI Repo / Benchmark Interest Rate percentage.
        inflation_rate_pct (Optional[Percentage]): CPI Inflation rate percentage.
        rbi_policy_stance (str): RBI monetary policy stance (HAWKISH, DOVISH, NEUTRAL).
        summary (str): Macroeconomic environment summary.
    """

    interest_rate_pct: Percentage | None = None
    inflation_rate_pct: Percentage | None = None
    rbi_policy_stance: str = "NEUTRAL"
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize MacroAnalysis to dictionary."""
        return {
            "interest_rate_pct": (
                self.interest_rate_pct.to_dict() if self.interest_rate_pct else None
            ),
            "inflation_rate_pct": (
                self.inflation_rate_pct.to_dict() if self.inflation_rate_pct else None
            ),
            "rbi_policy_stance": self.rbi_policy_stance,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MacroAnalysis":
        """Deserialize dictionary to MacroAnalysis."""
        return cls(
            interest_rate_pct=(
                Percentage.from_dict(data["interest_rate_pct"])
                if data.get("interest_rate_pct")
                else None
            ),
            inflation_rate_pct=(
                Percentage.from_dict(data["inflation_rate_pct"])
                if data.get("inflation_rate_pct")
                else None
            ),
            rbi_policy_stance=data.get("rbi_policy_stance", "NEUTRAL"),
            summary=data.get("summary", ""),
        )


@dataclass(frozen=True, slots=True)
class SentimentAnalysis:
    """
    Immutable value object for market news and SEBI filing sentiment evaluation.

    Attributes:
        news_sentiment (Optional[ConfidenceScore]): News stream sentiment score [0, 1].
        social_sentiment (Optional[ConfidenceScore]): Social sentiment score [0, 1].
        sebi_filing_sentiment (str): Sentiment classification from SEBI filings.
        summary (str): Sentiment analysis summary text.
    """

    news_sentiment: ConfidenceScore | None = None
    social_sentiment: ConfidenceScore | None = None
    sebi_filing_sentiment: str = "NEUTRAL"
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize SentimentAnalysis to dictionary."""
        return {
            "news_sentiment": self.news_sentiment.to_dict() if self.news_sentiment else None,
            "social_sentiment": self.social_sentiment.to_dict() if self.social_sentiment else None,
            "sebi_filing_sentiment": self.sebi_filing_sentiment,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SentimentAnalysis":
        """Deserialize dictionary to SentimentAnalysis."""
        return cls(
            news_sentiment=(
                ConfidenceScore.from_dict(data["news_sentiment"])
                if data.get("news_sentiment")
                else None
            ),
            social_sentiment=(
                ConfidenceScore.from_dict(data["social_sentiment"])
                if data.get("social_sentiment")
                else None
            ),
            sebi_filing_sentiment=data.get("sebi_filing_sentiment", "NEUTRAL"),
            summary=data.get("summary", ""),
        )
