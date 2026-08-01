"""
Asset Domain Entity for the Indian AI Hedge Fund Platform.

Represents a tradeable financial instrument (Equity, ETF, Mutual Fund, Derivative, etc.)
with tick size, lot size, and trade validation logic.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from packages.domain.enums.trading import AssetType
from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.isin import ISIN
from packages.domain.value_objects.identifiers.ticker import Ticker


@dataclass
class Asset:
    """
    Asset Domain Entity.

    Attributes:
        id (uuid.UUID): Unique asset identifier.
        ticker (Ticker): Ticker symbol.
        name (str): Instrument display name.
        asset_type (AssetType): Category (EQUITY, ETF, FUTURES, etc.).
        isin (Optional[ISIN]): ISIN code if applicable.
        lot_size (int): Standard minimum trade quantity / contract lot size.
        tick_size (Decimal): Minimum price fluctuation step (e.g. 0.05 INR for NSE).
        created_at (datetime): Creation timestamp (UTC).
        updated_at (datetime): Last update timestamp (UTC).
    """

    ticker: Ticker
    name: str
    asset_type: AssetType
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    isin: ISIN | None = None
    lot_size: int = 1
    tick_size: Decimal = Decimal("0.05")
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not isinstance(self.ticker, Ticker):
            object.__setattr__(self, "ticker", Ticker(self.ticker))
        if not isinstance(self.asset_type, AssetType):
            object.__setattr__(self, "asset_type", AssetType(self.asset_type))
        if self.isin is not None and not isinstance(self.isin, ISIN):
            object.__setattr__(self, "isin", ISIN(self.isin))

        if self.lot_size <= 0:
            raise ValidationError("Asset lot_size must be a positive integer (> 0).")

        dec_tick = to_decimal(self.tick_size)
        if dec_tick <= Decimal("0"):
            raise ValidationError("Asset tick_size must be strictly positive (> 0).")
        object.__setattr__(self, "tick_size", dec_tick)

        if self.created_at.tzinfo is None:
            object.__setattr__(self, "created_at", self.created_at.replace(tzinfo=UTC))
        if self.updated_at.tzinfo is None:
            object.__setattr__(self, "updated_at", self.updated_at.replace(tzinfo=UTC))

    def is_derivative(self) -> bool:
        """Return True if asset is a derivative contract."""
        return self.asset_type.is_derivative()

    def validate_order_quantity(self, quantity: Quantity) -> None:
        """
        Validate order share quantity against asset lot size rules.

        Raises:
            ValidationError: If quantity is zero or not a multiple of lot_size.
        """
        if quantity.is_zero():
            raise ValidationError("Order quantity cannot be zero.")

        if self.lot_size > 1:
            if Decimal(str(quantity.value)) % Decimal(str(self.lot_size)) != Decimal("0"):
                raise ValidationError(
                    f"Order quantity ({quantity.value}) must be a multiple of lot size ({self.lot_size}).",
                    context={"quantity": str(quantity.value), "lot_size": self.lot_size},
                )

    def validate_order_price(self, price: Price) -> None:
        """
        Validate limit order price against tick size rules.

        Raises:
            ValidationError: If price is not aligned to tick size multiples.
        """
        remainder = price.amount % self.tick_size
        if remainder != Decimal("0"):
            raise ValidationError(
                f"Order price ({price.amount}) does not align with asset tick size ({self.tick_size}).",
                context={"price": str(price.amount), "tick_size": str(self.tick_size)},
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize Asset entity to dictionary."""
        return {
            "id": str(self.id),
            "ticker": self.ticker.to_dict(),
            "name": self.name,
            "asset_type": self.asset_type.value,
            "isin": self.isin.to_dict() if self.isin else None,
            "lot_size": self.lot_size,
            "tick_size": str(self.tick_size),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Asset":
        """Deserialize dictionary to Asset entity."""
        isin_obj = ISIN.from_dict(data["isin"]) if data.get("isin") else None
        return cls(
            id=uuid.UUID(data["id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            name=data["name"],
            asset_type=AssetType(data["asset_type"]),
            isin=isin_obj,
            lot_size=int(data.get("lot_size", 1)),
            tick_size=Decimal(str(data.get("tick_size", "0.05"))),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Asset):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
