"""
Timestamp Value Objects for the Indian AI Hedge Fund Domain.

Provides Timestamp (strictly timezone-aware), MarketTimestamp, and TradingDate value objects.
Immutable, self-validating, zero naive datetime operations.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from packages.domain.enums.market import MarketSession
from packages.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class Timestamp:
    """
    Immutable value object for timezone-aware timestamps.

    Attributes:
        value (datetime): Timezone-aware datetime object (defaults to UTC).
    """

    value: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.value, datetime):
            raise ValidationError(
                f"Timestamp value must be a valid datetime instance (got {type(self.value).__name__})."
            )
        # Enforce timezone awareness
        if self.value.tzinfo is None or self.value.tzinfo.utcoffset(self.value) is None:
            # Convert naive datetime to UTC automatically for safety
            object.__setattr__(self, "value", self.value.replace(tzinfo=UTC))

    @classmethod
    def now_utc(cls) -> "Timestamp":
        """Construct Timestamp representing current time in UTC."""
        return cls(value=datetime.now(UTC))

    @classmethod
    def from_iso(cls, iso_str: str) -> "Timestamp":
        """Parse ISO-8601 string into a timezone-aware Timestamp."""
        try:
            dt = datetime.fromisoformat(iso_str)
            return cls(value=dt)
        except (ValueError, TypeError) as exc:
            raise ValidationError(
                f"Invalid ISO timestamp format: '{iso_str}'.",
                context={"iso_str": str(iso_str)},
            ) from exc

    @classmethod
    def from_isoformat(cls, iso_str: str) -> "Timestamp":
        """Alias for from_iso for standard library compatibility."""
        return cls.from_iso(iso_str)

    @property
    def iso_format(self) -> str:
        """Return ISO-8601 string representation."""
        return self.value.isoformat()

    def isoformat(self) -> str:
        """Return ISO-8601 string representation."""
        return self.value.isoformat()

    @property
    def date(self) -> date:
        """Return date component."""
        return self.value.date()

    def to_dict(self) -> str:
        """Serialize Timestamp to ISO-8601 string."""
        return self.value.isoformat()

    @classmethod
    def from_dict(cls, data: Any) -> "Timestamp":
        """Deserialize ISO-8601 string or dict to Timestamp."""
        if isinstance(data, dict):
            val_str = str(data.get("value") or data.get("timestamp") or "")
            return cls.from_iso(val_str)
        return cls.from_iso(str(data))


@dataclass(frozen=True, slots=True)
class MarketTimestamp:
    """
    Immutable value object for an exchange-specific trading timestamp.

    Attributes:
        timestamp (Timestamp): Base UTC timestamp.
        session (MarketSession): Active trading session phase.
    """

    timestamp: Timestamp
    session: MarketSession

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, Timestamp):
            object.__setattr__(self, "timestamp", Timestamp(self.timestamp))
        if not isinstance(self.session, MarketSession):
            object.__setattr__(self, "session", MarketSession(self.session))

    def is_regular_hours(self) -> bool:
        """Return True if session is normal continuous trading hours."""
        return self.session in (MarketSession.NORMAL, MarketSession.PRE_MARKET)

    def to_dict(self) -> dict[str, Any]:
        """Serialize MarketTimestamp to dictionary."""
        return {
            "timestamp": self.timestamp.iso_format,
            "session": self.session.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketTimestamp":
        """Deserialize dictionary to MarketTimestamp."""
        return cls(
            timestamp=Timestamp.from_iso(data["timestamp"]),
            session=MarketSession(data["session"]),
        )


@dataclass(frozen=True, slots=True)
class TradingDate:
    """
    Immutable value object representing an official exchange trading date (YYYY-MM-DD).

    Attributes:
        value (date): Pure date component.
    """

    value: date

    def __post_init__(self) -> None:
        if isinstance(self.value, datetime):
            object.__setattr__(self, "value", self.value.date())
        elif isinstance(self.value, str):
            try:
                object.__setattr__(self, "value", date.fromisoformat(self.value))
            except ValueError as exc:
                raise ValidationError(
                    f"Invalid TradingDate string format: '{self.value}'. Expected YYYY-MM-DD.",
                    context={"raw_value": str(self.value)},
                ) from exc
        elif not isinstance(self.value, date):
            raise ValidationError(
                f"TradingDate must be a valid date instance (got {type(self.value).__name__})."
            )

    def is_weekend(self) -> bool:
        """Return True if the date falls on Saturday (5) or Sunday (6)."""
        return self.value.weekday() >= 5

    @classmethod
    def today(cls) -> "TradingDate":
        """Construct TradingDate representing today's date."""
        return cls(value=datetime.now(UTC).date())

    def isoformat(self) -> str:
        """Return ISO-8601 YYYY-MM-DD string representation."""
        return self.value.isoformat()

    def to_dict(self) -> str:
        """Serialize TradingDate to ISO string."""
        return self.value.isoformat()

    @classmethod
    def from_dict(cls, data: Any) -> "TradingDate":
        """Deserialize string or dict to TradingDate."""
        if isinstance(data, dict):
            val_raw = data.get("value")
            if isinstance(val_raw, date):
                return cls(value=val_raw)
            return cls(value=date.fromisoformat(str(val_raw)))
        if isinstance(data, date):
            return cls(value=data)
        return cls(value=date.fromisoformat(str(data)))
