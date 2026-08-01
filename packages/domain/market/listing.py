"""
Listing Domain Entity for the Indian AI Hedge Fund Platform.

Represents a stock exchange listing linking a Company to a specific ExchangeType,
Ticker, and ISIN.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from packages.domain.enums.market import ExchangeType
from packages.domain.value_objects.identifiers.isin import ISIN
from packages.domain.value_objects.identifiers.ticker import Ticker


@dataclass
class Listing:
    """
    Listing Domain Entity.

    Attributes:
        id (uuid.UUID): Unique listing identifier.
        company_id (uuid.UUID): Parent company ID.
        exchange (ExchangeType): Exchange venue (NSE, BSE, etc.).
        ticker (Ticker): Ticker symbol value object.
        isin (ISIN): ISIN value object.
        is_primary (bool): Flag indicating if this is the primary listing.
        created_at (datetime): Creation timestamp (UTC).
        updated_at (datetime): Last update timestamp (UTC).
    """

    company_id: uuid.UUID
    exchange: ExchangeType
    ticker: Ticker
    isin: ISIN
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    is_primary: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not isinstance(self.exchange, ExchangeType):
            object.__setattr__(self, "exchange", ExchangeType(self.exchange))
        if not isinstance(self.ticker, Ticker):
            object.__setattr__(self, "ticker", Ticker(self.ticker))
        if not isinstance(self.isin, ISIN):
            object.__setattr__(self, "isin", ISIN(self.isin))

        if self.created_at.tzinfo is None:
            object.__setattr__(self, "created_at", self.created_at.replace(tzinfo=UTC))
        if self.updated_at.tzinfo is None:
            object.__setattr__(self, "updated_at", self.updated_at.replace(tzinfo=UTC))

    @property
    def full_symbol(self) -> str:
        """Return canonical exchange-qualified ticker symbol string."""
        return self.ticker.full_symbol

    def to_dict(self) -> dict[str, Any]:
        """Serialize Listing entity to dictionary."""
        return {
            "id": str(self.id),
            "company_id": str(self.company_id),
            "exchange": self.exchange.value,
            "ticker": self.ticker.to_dict(),
            "isin": self.isin.to_dict(),
            "is_primary": self.is_primary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Listing":
        """Deserialize dictionary to Listing entity."""
        return cls(
            id=uuid.UUID(data["id"]),
            company_id=uuid.UUID(data["company_id"]),
            exchange=ExchangeType(data["exchange"]),
            ticker=Ticker.from_dict(data["ticker"]),
            isin=ISIN.from_dict(data["isin"]),
            is_primary=data.get("is_primary", True),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Listing):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
