"""
TradingCalendar and TradingSession Domain Models for the Indian AI Hedge Fund Domain.

Provides market calendar schedules, holiday tracking, and trading session window evaluation.
Pure domain models with zero infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from packages.domain.enums.market import ExchangeType, MarketSession, MarketStatus
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.temporal.timestamps import Timestamp, TradingDate


@dataclass
class MarketHoliday:
    """
    Market Holiday Domain Model.

    Attributes:
        holiday_date (date): Date of declared market holiday.
        description (str): Description of the holiday (e.g. "Diwali Laxmi Pujan").
        is_trading_closed (bool): True if market is fully closed, False if special session.
        exchange (Optional[ExchangeType]): Exchange venue if specific.
    """

    holiday_date: date
    description: str
    is_trading_closed: bool = True
    exchange: ExchangeType | None = None

    def __post_init__(self) -> None:
        if isinstance(self.holiday_date, str):
            object.__setattr__(self, "holiday_date", date.fromisoformat(self.holiday_date))

    def to_dict(self) -> dict[str, Any]:
        """Serialize MarketHoliday to dictionary."""
        return {
            "holiday_date": self.holiday_date.isoformat(),
            "description": self.description,
            "is_trading_closed": self.is_trading_closed,
            "exchange": self.exchange.value if self.exchange else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketHoliday":
        """Deserialize dictionary to MarketHoliday."""
        ex = ExchangeType(data["exchange"]) if data.get("exchange") else None
        return cls(
            holiday_date=date.fromisoformat(data["holiday_date"]),
            description=data["description"],
            is_trading_closed=data.get("is_trading_closed", True),
            exchange=ex,
        )


@dataclass
class TradingSession:
    """
    Trading Session Window Model.

    Attributes:
        session_type (MarketSession): Type of session (PRE_MARKET, NORMAL, POST_MARKET).
        start_time (Timestamp): Session window start timestamp (UTC).
        end_time (Timestamp): Session window end timestamp (UTC).
    """

    session_type: MarketSession
    start_time: Timestamp
    end_time: Timestamp

    def __post_init__(self) -> None:
        if not isinstance(self.session_type, MarketSession):
            object.__setattr__(self, "session_type", MarketSession(self.session_type))
        if not isinstance(self.start_time, Timestamp):
            object.__setattr__(self, "start_time", Timestamp(self.start_time))
        if not isinstance(self.end_time, Timestamp):
            object.__setattr__(self, "end_time", Timestamp(self.end_time))

        if self.start_time.value >= self.end_time.value:
            raise ValidationError("TradingSession start_time must be strictly before end_time.")

    def contains(self, ts: Timestamp) -> bool:
        """Return True if timestamp falls within session window [start_time, end_time]."""
        return bool(self.start_time.value <= ts.value <= self.end_time.value)

    def to_dict(self) -> dict[str, Any]:
        """Serialize TradingSession to dictionary."""
        return {
            "session_type": self.session_type.value,
            "start_time": self.start_time.to_dict(),
            "end_time": self.end_time.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradingSession":
        """Deserialize dictionary to TradingSession."""
        return cls(
            session_type=MarketSession(data["session_type"]),
            start_time=Timestamp.from_dict(data["start_time"]),
            end_time=Timestamp.from_dict(data["end_time"]),
        )


@dataclass
class TradingCalendar:
    """
    Trading Calendar Domain Model.

    Attributes:
        exchange (ExchangeType): Exchange venue (NSE, BSE, etc.).
        holidays (List[MarketHoliday]): List of declared market holidays.
        sessions (List[TradingSession]): Configured daily trading session windows.
    """

    exchange: ExchangeType
    holidays: list[MarketHoliday] = field(default_factory=list)
    sessions: list[TradingSession] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.exchange, ExchangeType):
            object.__setattr__(self, "exchange", ExchangeType(self.exchange))

    def is_trading_day(self, trading_date: TradingDate) -> bool:
        """
        Return True if the date is a valid trading day (not a weekend and not a holiday).
        """
        if trading_date.value.weekday() >= 5:
            return False

        for h in self.holidays:
            if h.holiday_date == trading_date.value and h.is_trading_closed:
                return False
        return True

    def get_market_status(self, timestamp: Timestamp) -> MarketStatus:
        """
        Evaluate current MarketStatus for a given timestamp based on calendar sessions & holidays.
        """
        dt = timestamp.value.date()
        t_date = TradingDate(dt)

        if not self.is_trading_day(t_date):
            return MarketStatus.CLOSED

        for s in self.sessions:
            if s.contains(timestamp):
                if s.session_type == MarketSession.PRE_MARKET:
                    return MarketStatus.PRE_OPEN
                if s.session_type == MarketSession.NORMAL:
                    return MarketStatus.OPEN
                if s.session_type in (MarketSession.POST_MARKET, MarketSession.SPECIAL):
                    return MarketStatus.POST_CLOSE

        return MarketStatus.CLOSED

    def to_dict(self) -> dict[str, Any]:
        """Serialize TradingCalendar to dictionary."""
        return {
            "exchange": self.exchange.value,
            "holidays": [h.to_dict() for h in self.holidays],
            "sessions": [s.to_dict() for s in self.sessions],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradingCalendar":
        """Deserialize dictionary to TradingCalendar."""
        return cls(
            exchange=ExchangeType(data["exchange"]),
            holidays=[MarketHoliday.from_dict(h) for h in data.get("holidays", [])],
            sessions=[TradingSession.from_dict(s) for s in data.get("sessions", [])],
        )
