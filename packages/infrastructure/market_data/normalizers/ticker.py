"""
Ticker Normalizer for Market Data Infrastructure.

Converts domain Ticker objects and exchange symbols into vendor-specific symbol strings,
and vice versa. Supports NSE (.NS), BSE (.BO), MCX, ETFs, and global exchanges.
"""

from packages.domain.enums.market import ExchangeType
from packages.domain.value_objects.identifiers.ticker import Ticker


class TickerNormalizer:
    """
    Normalizes domain Ticker instances to provider symbol formats and vice versa.
    """

    _EXCHANGE_SUFFIX_MAP: dict[ExchangeType, str] = {
        ExchangeType.NSE: ".NS",
        ExchangeType.BSE: ".BO",
        ExchangeType.MCX: ".MCX",
        ExchangeType.NYSE: "",
        ExchangeType.NASDAQ: "",
        ExchangeType.LSE: ".L",
    }

    _REVERSE_SUFFIX_MAP: dict[str, ExchangeType] = {
        ".NS": ExchangeType.NSE,
        ".BO": ExchangeType.BSE,
        ".MCX": ExchangeType.MCX,
        ".L": ExchangeType.LSE,
    }

    @classmethod
    def to_provider_symbol(
        cls,
        ticker: Ticker,
        provider: str = "yahoo",
    ) -> str:
        """
        Convert a domain Ticker into a vendor-specific symbol string.
        """
        base_symbol = ticker.symbol.upper()
        exchange = ticker.exchange

        if provider.lower() in ("yfinance", "yahoo"):
            suffix = cls._EXCHANGE_SUFFIX_MAP.get(exchange, "") if exchange is not None else ""
            if suffix and not base_symbol.endswith(suffix):
                return f"{base_symbol}{suffix}"
            return base_symbol

        if provider.lower() in ("nse", "bse"):
            return base_symbol

        return base_symbol

    @classmethod
    def from_provider_symbol(
        cls,
        symbol: str,
        default_exchange: ExchangeType = ExchangeType.NSE,
    ) -> Ticker:
        """
        Convert a vendor symbol string back into a domain Ticker value object.
        """
        clean_symbol = symbol.strip().upper()

        for suffix, exchange in cls._REVERSE_SUFFIX_MAP.items():
            if clean_symbol.endswith(suffix):
                raw_base = clean_symbol[: -len(suffix)]
                return Ticker(f"{raw_base}.{exchange.value}")

        if "." in clean_symbol:
            parts = clean_symbol.split(".")
            return Ticker(f"{parts[0]}.{parts[1]}")

        return Ticker(f"{clean_symbol}.{default_exchange.value}")
