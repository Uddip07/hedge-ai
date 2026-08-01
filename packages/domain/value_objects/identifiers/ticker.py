"""
Ticker Value Object for the Indian AI Hedge Fund Domain.

Represents a stock, index, derivative, or commodity ticker symbol, bound optionally
to an ExchangeType enum. Immutable and self-validating.
"""

from dataclasses import dataclass
from typing import Any

from packages.domain.enums.market import ExchangeType
from packages.domain.utils.validation import validate_ticker_format


@dataclass(frozen=True, slots=True)
class Ticker:
    """
    Immutable value object representing a financial market ticker.

    Attributes:
        symbol (str): Base ticker symbol (e.g. 'RELIANCE', 'INFY').
        exchange (Optional[ExchangeType]): Exchange venue (e.g. ExchangeType.NSE).
    """

    symbol: str
    exchange: ExchangeType | None = None

    def __post_init__(self) -> None:
        raw = self.symbol
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError("Ticker symbol must be a non-empty string.")

        # Normalize symbol string
        cleaned = validate_ticker_format(raw)

        # If ticker was provided as 'RELIANCE.NSE', extract exchange automatically if missing
        parsed_symbol = cleaned
        parsed_exchange = self.exchange

        if "." in cleaned:
            parts = cleaned.split(".", 1)
            parsed_symbol = parts[0]
            if parsed_exchange is None:
                try:
                    parsed_exchange = ExchangeType(parts[1])
                except ValueError:
                    pass
        elif ":" in cleaned:
            parts = cleaned.split(":", 1)
            parsed_symbol = parts[0]
            if parsed_exchange is None:
                try:
                    parsed_exchange = ExchangeType(parts[1])
                except ValueError:
                    pass

        # Use object.__setattr__ due to frozen dataclass
        object.__setattr__(self, "symbol", parsed_symbol)
        object.__setattr__(self, "exchange", parsed_exchange)

    @property
    def full_symbol(self) -> str:
        """Return canonical formatted ticker string (e.g., 'RELIANCE.NSE')."""
        if self.exchange:
            return f"{self.symbol}.{self.exchange.value}"
        return self.symbol

    def is_indian(self) -> bool:
        """Return True if the ticker is listed on an Indian exchange."""
        if self.exchange:
            return self.exchange.is_indian_exchange()
        return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize value object to dictionary."""
        return {
            "symbol": self.symbol,
            "exchange": self.exchange.value if self.exchange else None,
            "full_symbol": self.full_symbol,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ticker":
        """Deserialize dictionary payload to Ticker value object."""
        exchange_raw = data.get("exchange")
        exchange = ExchangeType(exchange_raw) if exchange_raw else None
        return cls(symbol=data["symbol"], exchange=exchange)

    def __str__(self) -> str:
        return self.full_symbol
