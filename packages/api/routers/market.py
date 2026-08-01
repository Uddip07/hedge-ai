"""
Market Data Router.

Provides GET /market/{ticker} endpoint for fetching current market quotes and company profile data.
"""

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status

from packages.api.dependencies import get_market_data_port
from packages.application.ports.market_data_port import MarketDataPort
from packages.domain.enums.market import ExchangeType
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.identifiers.ticker import Ticker

router = APIRouter(prefix="/market", tags=["Market Data"])


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
    """
    Fetch market quote for a given ticker symbol string.

    Args:
        ticker (str): Ticker symbol string (e.g. 'RELIANCE', 'RELIANCE.NSE', 'TCS.BSE').
        refresh (bool): Query parameter to invalidate cache and force live provider fetch.
        market_data_port (MarketDataPort): Injected market data port.

    Returns:
        dict[str, Any]: Market data payload.
    """
    clean_ticker = ticker.strip().upper()
    if not clean_ticker:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ticker symbol cannot be empty.",
        )
    if clean_ticker.startswith("^"):
        if clean_ticker in ("^NSEI", "^NSEBANK", "^BSESN"):
            clean_ticker = clean_ticker
    elif clean_ticker in ("NIFTY", "NIFTY50", "NIFTY 50"):
        clean_ticker = "NIFTY.NSE"
    elif clean_ticker in ("BANKNIFTY", "BANK NIFTY"):
        clean_ticker = "BANKNIFTY.NSE"
    elif clean_ticker in ("SENSEX",):
        clean_ticker = "SENSEX.BSE"
    elif "." not in clean_ticker:
        clean_ticker = f"{clean_ticker}.NSE"

    try:
        if clean_ticker.startswith("^"):
            # Special index representation
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
