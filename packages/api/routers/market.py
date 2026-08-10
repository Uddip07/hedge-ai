"""
Market Data Router.

Provides GET /market/{ticker} endpoint for fetching current market quotes and company profile data,
and GET /market/{ticker}/history for retrieving historical OHLCV candles.
"""

import uuid
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from packages.api.dependencies import get_market_data_port, verify_automation_key
from packages.application.ports.market_data_port import MarketDataPort
from packages.domain.enums.market import ExchangeType, Timeframe
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp

router = APIRouter(prefix="/market", tags=["Market Data"])


def _to_float(val: Any) -> float:
    if hasattr(val, "amount"):
        return float(val.amount)
    if hasattr(val, "value"):
        return float(val.value)
    return float(val)


def _normalize_ticker_symbol(ticker: str) -> str:
    clean_ticker = ticker.strip().upper()
    if not clean_ticker:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ticker symbol cannot be empty.",
        )
    if clean_ticker.startswith("^"):
        if clean_ticker in ("^NSEI", "^NSEBANK", "^BSESN"):
            return clean_ticker
    elif clean_ticker in ("NIFTY", "NIFTY50", "NIFTY 50"):
        return "NIFTY.NSE"
    elif clean_ticker in ("BANKNIFTY", "BANK NIFTY"):
        return "BANKNIFTY.NSE"
    elif clean_ticker in ("SENSEX",):
        return "SENSEX.BSE"
    elif "." not in clean_ticker:
        return f"{clean_ticker}.NSE"
    return clean_ticker


@router.get(
    "/{ticker}",
    status_code=status.HTTP_200_OK,
    summary="Get Market Data Quote",
    description="Retrieve current market price quote, exchange status, and company profile for a given asset ticker.",
)
async def get_market_data(
    ticker: str,
    refresh: bool = False,
    market_data_port: MarketDataPort = Depends(get_market_data_port),
) -> dict[str, Any]:
    clean_ticker = _normalize_ticker_symbol(ticker)

    try:
        if clean_ticker.startswith("^"):
            base_sym = clean_ticker.lstrip("^")
            t = Ticker(f"{base_sym}.NSE")
        else:
            t = Ticker(clean_ticker)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid ticker symbol format: '{ticker}'.",
        ) from exc

    exch = t.exchange or ExchangeType.NSE
    profile = market_data_port.get_company_profile(t)

    if hasattr(market_data_port, "manager"):
        quote = market_data_port.manager.get_quote(t, force_refresh=refresh)
    else:
        price = market_data_port.get_latest_price(t)
        is_open = market_data_port.is_market_open(exch)
        return {
            "ticker": t.full_symbol,
            "symbol": t.symbol,
            "exchange": exch.value,
            "price": str(price.amount),
            "change": "0.00",
            "change_percent": "0.00",
            "volume": "0.00",
            "open": str(price.amount),
            "high": str(price.amount),
            "low": str(price.amount),
            "previous_close": str(price.amount),
            "currency": price.money.currency.code,
            "timestamp": t.symbol,
            "market_status": "OPEN" if is_open else "CLOSED",
            "is_market_open": is_open,
            "company_name": profile.name if profile else t.symbol,
            "sector": profile.sector.value if profile else "LARGE_CAP",
            "industry": profile.industry if profile else "General",
        }

    res = cast(dict[str, Any], quote.to_dict())
    res.update(
        {
            "company_name": profile.name if profile else t.symbol,
            "sector": profile.sector.value if profile else "LARGE_CAP",
            "industry": profile.industry if profile else "General",
        }
    )
    return res


@router.get(
    "/{ticker}/history",
    status_code=status.HTTP_200_OK,
    summary="Get Historical Market Data Candles",
    description="Retrieve historical OHLCV price series candles from backend provider.",
)
async def get_market_history(
    ticker: str,
    market_data_port: MarketDataPort = Depends(get_market_data_port),
) -> list[dict[str, Any]]:
    clean_ticker = _normalize_ticker_symbol(ticker)

    try:
        if clean_ticker.startswith("^"):
            base_sym = clean_ticker.lstrip("^")
            t = Ticker(f"{base_sym}.NSE")
        else:
            t = Ticker(clean_ticker)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid ticker symbol format: '{ticker}'.",
        ) from exc

    candles: list[Any] = []
    if hasattr(market_data_port, "manager"):
        now = Timestamp.now_utc()
        start = Timestamp.from_iso("2020-01-01T00:00:00+00:00")
        candles = market_data_port.manager.get_historical_candles(t, Timeframe.DAY_1, start, now)

    result: list[dict[str, Any]] = []
    for c in candles:
        if hasattr(c, "to_dict"):
            result.append(c.to_dict())
        else:
            result.append(
                {
                    "date": str(getattr(c, "timestamp", getattr(c, "date", ""))),
                    "open": float(getattr(c, "open", 0.0)),
                    "high": float(getattr(c, "high", 0.0)),
                    "low": float(getattr(c, "low", 0.0)),
                    "close": float(getattr(c, "close", getattr(c, "price", 0.0))),
                    "volume": float(getattr(c, "volume", 0.0)),
                }
            )

    return result


@router.get(
    "/summary/daily",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_automation_key)],
    summary="Get Daily Market Performance Summary",
    description="Generate structured daily market summary covering NIFTY, benchmark indices, sector performance, top gainers, top losers, and volume.",
)
async def get_daily_market_summary() -> dict[str, Any]:
    """
    Produce daily market closing/intraday structured performance summary from real provider data.
    """
    from datetime import UTC, datetime

    from packages.infrastructure.database.models import SystemMetadataModel
    from packages.infrastructure.database.session import DatabaseManager
    from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider

    provider = YahooMarketDataProvider()
    now_utc = datetime.now(UTC)

    # 1. Benchmark Quotes
    benchmarks: dict[str, Any] = {}
    for sym, name in [("^NSEI", "NIFTY 50"), ("^NSEBANK", "BANK NIFTY"), ("^BSESN", "SENSEX")]:
        try:
            q = provider.get_quote(Ticker(sym))
            price_val = str(getattr(q.price, "amount", getattr(q.price, "value", q.price)))
            change_val = str(getattr(q, "change_24h", getattr(q, "change", "0.0")))
            benchmarks[name] = {
                "symbol": sym,
                "price": price_val,
                "change": change_val,
                "change_percent": change_val,
                "timestamp": str(q.timestamp),
            }
        except Exception as exc:
            benchmarks[name] = {"symbol": sym, "error": str(exc)}

    # 2. Major Stock Quotes for Gainers / Losers
    tracked_stocks = [
        "RELIANCE.NSE",
        "TCS.NSE",
        "INFY.NSE",
        "HDFCBANK.NSE",
        "ICICIBANK.NSE",
        "SBIN.NSE",
        "BHARTIARTL.NSE",
        "ITC.NSE",
        "KOTAKBANK.NSE",
        "LT.NSE",
        "HINDUNILVR.NSE",
        "TATAMOTORS.NSE",
        "AXISBANK.NSE",
        "SUNPHARMA.NSE",
        "MARUTI.NSE",
    ]
    stock_quotes: list[dict[str, Any]] = []
    for s in tracked_stocks:
        try:
            q = provider.get_quote(Ticker(s))
            price_f = _to_float(q.price)
            change_f = float(getattr(q, "change_24h", getattr(q, "change", 0.0)))
            vol_f = float(getattr(q, "volume_24h", getattr(q, "volume", 0.0)))
            stock_quotes.append(
                {
                    "ticker": s,
                    "symbol": s.split(".")[0],
                    "price": price_f,
                    "change": change_f,
                    "change_percent": change_f,
                    "volume": vol_f,
                }
            )
        except Exception:
            continue

    # Sort gainers and losers
    sorted_by_change = sorted(stock_quotes, key=lambda x: x["change_percent"], reverse=True)
    top_gainers = sorted_by_change[:5]
    top_losers = sorted_by_change[-5:][::-1] if len(sorted_by_change) >= 5 else []

    # 3. Sector Performance
    try:
        sectors = provider.get_sector_performance()
    except Exception:
        sectors = {}

    summary = {
        "report_date": now_utc.strftime("%Y-%m-%d"),
        "timestamp": now_utc.isoformat(),
        "benchmarks": benchmarks,
        "sector_performance": sectors,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "market_breadth": {
            "advances": len([s for s in stock_quotes if s["change_percent"] > 0]),
            "declines": len([s for s in stock_quotes if s["change_percent"] < 0]),
            "unchanged": len([s for s in stock_quotes if s["change_percent"] == 0]),
            "total_tracked": len(stock_quotes),
        },
    }

    # Persist summary to system metadata
    try:
        import json

        db = DatabaseManager()
        with db.session() as session:
            key_name = f"market_summary_{now_utc.strftime('%Y_%m_%d')}"
            existing = session.scalar(
                select(SystemMetadataModel).where(SystemMetadataModel.key == key_name)
            )
            if existing:
                existing.value = json.dumps(summary)
                existing.updated_at = now_utc
            else:
                session.add(
                    SystemMetadataModel(
                        id=str(uuid.uuid4()),
                        key=key_name,
                        value=json.dumps(summary),
                        description="Daily Market Summary Snapshot",
                        updated_at=now_utc,
                    )
                )
    except Exception:
        pass

    return summary


@router.post(
    "/news/ingest",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_automation_key)],
    summary="Ingest & Deduplicate News Articles",
    description="Fetch live news for tickers from Yahoo Finance, deduplicate by URL/title, evaluate real AI sentiment if configured, and return structured articles.",
)
async def ingest_news(
    tickers: list[str] | None = None,
) -> dict[str, Any]:
    """
    Fetch, deduplicate, and process financial news headlines from Yahoo Finance.
    """
    from packages.ai.agents.news_agent import NewsAgent
    from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider

    provider = YahooMarketDataProvider()
    target_tickers = tickers or [
        "RELIANCE",
        "TCS",
        "INFY",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "NIFTY",
    ]

    all_articles: list[dict[str, Any]] = []
    seen_identifiers: set[str] = set()

    news_agent = NewsAgent()

    for raw_ticker in target_tickers:
        clean = _normalize_ticker_symbol(raw_ticker)
        try:
            t = Ticker(clean) if not clean.startswith("^") else Ticker(f"{clean.lstrip('^')}.NSE")
            articles = provider.get_news(t)
            for art in articles:
                identifier = (art.url or art.title).strip().lower()
                if not identifier or identifier in seen_identifiers:
                    continue
                seen_identifiers.add(identifier)

                # Sentiment analysis from provider / model (no fabricated fake numbers)
                sentiment_score: float | None = (
                    float(art.sentiment_score) if art.sentiment_score is not None else None
                )
                sentiment_label: str = (
                    "UNAVAILABLE"
                    if sentiment_score is None
                    else (
                        "POSITIVE"
                        if sentiment_score > 0.6
                        else ("NEGATIVE" if sentiment_score < 0.4 else "NEUTRAL")
                    )
                )

                all_articles.append(
                    {
                        "ticker": t.full_symbol,
                        "title": art.title,
                        "summary": art.content,
                        "source": art.source,
                        "url": art.url,
                        "published_at": art.published_at,
                        "sentiment_score": sentiment_score,
                        "sentiment_label": sentiment_label,
                    }
                )
        except Exception:
            continue

    return {
        "status": "COMPLETED",
        "tickers_queried": target_tickers,
        "articles_count": len(all_articles),
        "articles": all_articles,
    }


@router.get(
    "/{ticker}/news",
    status_code=status.HTTP_200_OK,
    summary="Get News for Single Ticker",
    description="Retrieve live Yahoo Finance news articles and sentiment for a single ticker.",
)
async def get_ticker_news(ticker: str) -> list[dict[str, Any]]:
    """Get news articles for a single asset symbol."""
    clean_ticker = _normalize_ticker_symbol(ticker)
    t = (
        Ticker(clean_ticker)
        if not clean_ticker.startswith("^")
        else Ticker(f"{clean_ticker.lstrip('^')}.NSE")
    )

    from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider

    provider = YahooMarketDataProvider()
    raw_articles = provider.get_news(t)

    return [
        {
            "ticker": t.full_symbol,
            "title": a.title,
            "content": a.content,
            "source": a.source,
            "url": a.url,
            "published_at": a.published_at,
            "sentiment_score": a.sentiment_score,
        }
        for a in raw_articles
    ]
