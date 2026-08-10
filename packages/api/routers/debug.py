from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from packages.api.dependencies import verify_automation_key
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.logging import get_logger
from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider

logger = get_logger(name="ihf_ai.api.routers.debug")

router = APIRouter(prefix="/debug", tags=["Diagnostics"])


@router.get(
    "/provider/{ticker}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_automation_key)],
    summary="Debug Market Data Provider Payload",
    description="Inspect raw yfinance provider response, resolved symbol, normalized quote, and validation log for a given ticker.",
)
async def debug_provider_payload(ticker: str) -> dict[str, Any]:
    """
    Diagnostic endpoint to validate Yahoo Finance live quote normalization.
    """
    clean_ticker = ticker.strip().upper()
    if not clean_ticker:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ticker symbol cannot be empty.",
        )

    if clean_ticker.startswith("^"):
        resolved_symbol = clean_ticker
        base_sym = clean_ticker.lstrip("^")
        t = Ticker(f"{base_sym}.NSE")
    elif clean_ticker in ("NIFTY", "NIFTY50", "NIFTY 50"):
        resolved_symbol = "^NSEI"
        t = Ticker("NIFTY.NSE")
    elif clean_ticker in ("BANKNIFTY", "BANK NIFTY"):
        resolved_symbol = "^NSEBANK"
        t = Ticker("BANKNIFTY.NSE")
    elif clean_ticker in ("SENSEX",):
        resolved_symbol = "^BSESN"
        t = Ticker("SENSEX.BSE")
    else:
        if "." not in clean_ticker:
            clean_ticker = f"{clean_ticker}.NSE"
        try:
            t = Ticker(clean_ticker)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid ticker symbol format: '{ticker}'.",
            ) from exc

        provider_inst = YahooMarketDataProvider()
        resolved_symbol = provider_inst._resolve_yf_symbol(t)

    normalization_log: list[str] = []
    raw_payload: dict[str, Any] = {}

    try:
        import yfinance as yf

        t_obj = yf.Ticker(resolved_symbol)
        fast_info = getattr(t_obj, "fast_info", {})
        info = getattr(t_obj, "info", {})

        last_price = getattr(fast_info, "last_price", None) or getattr(
            fast_info, "previous_close", None
        )
        prev_close = getattr(fast_info, "previous_close", None) or last_price
        open_price = getattr(fast_info, "open", None) or last_price
        high_price = getattr(fast_info, "day_high", None) or last_price
        low_price = getattr(fast_info, "day_low", None) or last_price
        vol = getattr(fast_info, "last_volume", None) or 0.0

        raw_payload = {
            "resolved_symbol": resolved_symbol,
            "last_price": str(last_price) if last_price is not None else None,
            "previous_close": str(prev_close) if prev_close is not None else None,
            "open": str(open_price) if open_price is not None else None,
            "day_high": str(high_price) if high_price is not None else None,
            "day_low": str(low_price) if low_price is not None else None,
            "last_volume": str(vol),
            "currency": getattr(fast_info, "currency", "INR"),
            "long_name": info.get("longName") or info.get("shortName"),
            "quote_type": info.get("quoteType"),
            "market_state": getattr(fast_info, "market_state", "REGULAR"),
        }
    except Exception as err:
        logger.error(
            f"Failed to fetch raw yfinance metadata for {resolved_symbol}: {err}", exc_info=True
        )
        normalization_log.append("Failed to fetch raw yfinance metadata: upstream provider error.")

    try:
        provider = YahooMarketDataProvider()
        quote = provider.get_quote(t)
        normalized_dict = quote.to_dict()
        normalization_log.append(
            "Normalized quote constructed successfully via YahooMarketDataProvider."
        )
    except Exception as err:
        logger.error(f"Failed to normalize quote for {t.symbol}: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to normalize quote from market data provider.",
        ) from None

    return {
        "provider": "YahooFinance",
        "requested_symbol": ticker,
        "resolved_symbol": resolved_symbol,
        "raw_payload": raw_payload,
        "normalized_quote": normalized_dict,
        "normalization_log": normalization_log,
    }
