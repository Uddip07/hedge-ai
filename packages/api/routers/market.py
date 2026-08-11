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
    if val is None:
        return 0.0
    if hasattr(val, "amount"):
        return float(val.amount)
    if hasattr(val, "value"):
        return float(val.value)
    if isinstance(val, dict):
        if "amount" in val:
            return float(val["amount"])
        if "money" in val and isinstance(val["money"], dict) and "amount" in val["money"]:
            return float(val["money"]["amount"])
        if "value" in val:
            return float(val["value"])
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


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
    elif clean_ticker in ("NIFTY", "NIFTY50", "NIFTY 50", "NIFTY.NSE"):
        return "NIFTY.NSE"
    elif clean_ticker in ("BANKNIFTY", "BANK NIFTY", "BANKNIFTY.NSE"):
        return "BANKNIFTY.NSE"
    elif clean_ticker in ("SENSEX", "SENSEX.BSE"):
        return "SENSEX.BSE"
    elif clean_ticker.endswith(".NS"):
        return f"{clean_ticker[:-3]}.NSE"
    elif clean_ticker.endswith(".BO"):
        return f"{clean_ticker[:-3]}.BSE"
    elif "." not in clean_ticker:
        return f"{clean_ticker}.NSE"
    return clean_ticker


def _format_ts(ts: Any) -> tuple[str, str]:
    if hasattr(ts, "isoformat") and callable(ts.isoformat):
        iso_s = ts.isoformat()
    elif hasattr(ts, "value") and hasattr(ts.value, "isoformat"):
        iso_s = ts.value.isoformat()
    elif isinstance(ts, dict):
        iso_s = str(ts.get("iso") or ts.get("timestamp") or ts.get("value") or "")
    else:
        iso_s = str(ts)
    date_s = iso_s[:10] if len(iso_s) >= 10 and "-" in iso_s[:10] else iso_s
    return iso_s, date_s


@router.get(
    "/{ticker}",
    status_code=status.HTTP_200_OK,
    summary="Get Market Data Quote",
    description="Retrieve current canonical market price quote, exchange status, and company profile for a given asset ticker.",
)
async def get_market_data(
    ticker: str,
    refresh: bool = False,
    market_data_port: MarketDataPort = Depends(get_market_data_port),
) -> dict[str, Any]:
    from datetime import datetime, timedelta, timezone

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

    # Name resolution
    default_name = t.symbol
    if t.symbol in ("NIFTY", "NIFTY50", "NIFTY.NSE", "^NSEI"):
        default_name = "NIFTY 50"
    elif t.symbol in ("BANKNIFTY", "BANKNIFTY.NSE", "^NSEBANK"):
        default_name = "BANK NIFTY"
    elif t.symbol in ("SENSEX", "SENSEX.BSE", "^BSESN"):
        default_name = "SENSEX"

    company_name = profile.name if profile else default_name
    sector = profile.sector.value if profile and hasattr(profile.sector, "value") else "LARGE_CAP"
    industry = profile.industry if profile else "General"

    if hasattr(market_data_port, "manager"):
        quote = market_data_port.manager.get_quote(t, force_refresh=refresh)
    else:
        price = market_data_port.get_latest_price(t)
        is_open = market_data_port.is_market_open(exch)
        price_f = _to_float(price)
        ist = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
        return {
            "symbol": t.symbol,
            "ticker": t.full_symbol,
            "yahoo_symbol": getattr(t, "yahoo_symbol", ""),
            "exchange": exch.value,
            "name": company_name,
            "price": price_f,
            "previous_close": price_f,
            "change": 0.0,
            "change_percent": 0.0,
            "open": price_f,
            "high": price_f,
            "low": price_f,
            "volume": 0,
            "currency": price.money.currency.code if hasattr(price, "money") else "INR",
            "timestamp": Timestamp.now_utc().isoformat(),
            "timestamp_ist": now_ist,
            "market_state": "OPEN" if is_open else "CLOSED",
            "is_market_open": is_open,
            "source": "FALLBACK",
            "company_name": company_name,
            "sector": sector,
            "industry": industry,
        }

    raw_dict = cast(dict[str, Any], quote.to_dict()) if hasattr(quote, "to_dict") else {}
    price_val = _to_float(getattr(quote, "price", raw_dict.get("price", 0.0)))
    prev_close_val = _to_float(
        getattr(quote, "previous_close", raw_dict.get("previous_close", price_val))
    )
    if prev_close_val == 0.0:
        prev_close_val = price_val

    change_val = _to_float(
        getattr(quote, "change", raw_dict.get("change", price_val - prev_close_val))
    )
    change_pct_val = _to_float(
        getattr(
            quote,
            "change_percent",
            raw_dict.get(
                "change_percent",
                ((change_val / prev_close_val) * 100) if prev_close_val > 0 else 0.0,
            ),
        )
    )

    open_val = _to_float(getattr(quote, "open", raw_dict.get("open", price_val)))
    high_val = _to_float(getattr(quote, "high", raw_dict.get("high", price_val)))
    low_val = _to_float(getattr(quote, "low", raw_dict.get("low", price_val)))
    vol_val = _to_float(getattr(quote, "volume", raw_dict.get("volume", 0.0)))

    status_str = str(getattr(quote, "market_status", raw_dict.get("market_status", "CLOSED")))
    if hasattr(status_str, "value"):
        status_str = status_str.value
    is_open = status_str == "OPEN" or getattr(
        quote, "is_market_open", raw_dict.get("is_market_open", False)
    )

    source_str = str(getattr(quote, "source", raw_dict.get("source", "YAHOO_LAST_CLOSE")))
    yahoo_sym = str(getattr(quote, "yahoo_symbol", raw_dict.get("yahoo_symbol", "")))
    if not yahoo_sym and hasattr(market_data_port, "manager"):
        primary = getattr(market_data_port.manager, "primary", None)
        if primary and hasattr(primary, "_resolve_yf_symbol"):
            yahoo_sym = primary._resolve_yf_symbol(t)

    ts_val = getattr(quote, "timestamp", raw_dict.get("timestamp"))
    ts_iso, _ = _format_ts(ts_val or Timestamp.now_utc())

    ist = timezone(timedelta(hours=5, minutes=30))
    try:
        ts_inner = getattr(ts_val, "value", None)
        if isinstance(ts_inner, datetime):
            quote_dt_ist = ts_inner.astimezone(ist)
        elif isinstance(ts_val, datetime):
            quote_dt_ist = ts_val.astimezone(ist)
        else:
            quote_dt = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
            quote_dt_ist = quote_dt.astimezone(ist)
        quote_ist_str = quote_dt_ist.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        quote_ist_str = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")

    server_clock_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")

    return {
        "symbol": t.symbol,
        "ticker": t.full_symbol,
        "yahoo_symbol": yahoo_sym,
        "exchange": exch.value,
        "name": company_name,
        "price": price_val,
        "previous_close": prev_close_val,
        "change": round(change_val, 2),
        "change_percent": round(change_pct_val, 2),
        "open": open_val,
        "high": high_val,
        "low": low_val,
        "volume": int(vol_val),
        "currency": str(raw_dict.get("currency", "INR")),
        "timestamp": ts_iso,
        "timestamp_ist": quote_ist_str,
        "quote_timestamp": ts_iso,
        "system_clock": server_clock_ist,
        "market_state": status_str,
        "is_market_open": is_open,
        "source": source_str,
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
    }


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
        if hasattr(c, "open") and hasattr(c, "close"):
            ts_iso, date_str = _format_ts(c.timestamp)
            result.append(
                {
                    "date": date_str,
                    "timestamp": ts_iso,
                    "open": _to_float(c.open),
                    "high": _to_float(c.high),
                    "low": _to_float(c.low),
                    "close": _to_float(c.close),
                    "volume": _to_float(c.volume),
                }
            )
        elif isinstance(c, dict):
            ohlcv_dict = c.get("ohlcv", c)
            raw_ts = c.get("date", c.get("timestamp", ""))
            ts_iso, date_str = _format_ts(raw_ts)
            result.append(
                {
                    "date": date_str,
                    "timestamp": ts_iso,
                    "open": _to_float(ohlcv_dict.get("open", 0.0)),
                    "high": _to_float(ohlcv_dict.get("high", 0.0)),
                    "low": _to_float(ohlcv_dict.get("low", 0.0)),
                    "close": _to_float(ohlcv_dict.get("close", 0.0)),
                    "volume": _to_float(ohlcv_dict.get("volume", 0.0)),
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
