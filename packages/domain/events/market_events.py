"""
Market Domain Events for the Indian AI Hedge Fund Platform.

Event definitions for market sessions, price updates, and OHLCV bar closes.
"""

import uuid
from dataclasses import dataclass
from typing import Any

from packages.domain.enums.market import ExchangeType, MarketSession
from packages.domain.events.base import DomainEvent
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class MarketSessionChangedEvent(DomainEvent):
    """
    Emitted when an exchange market operational session changes (e.g. PRE_MARKET to NORMAL).
    """

    exchange: ExchangeType
    previous_session: MarketSession
    new_session: MarketSession

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "exchange": self.exchange.value,
                "previous_session": self.previous_session.value,
                "new_session": self.new_session.value,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketSessionChangedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            exchange=ExchangeType(data["exchange"]),
            previous_session=MarketSession(data["previous_session"]),
            new_session=MarketSession(data["new_session"]),
        )


@dataclass(frozen=True, kw_only=True)
class PriceUpdatedEvent(DomainEvent):
    """
    Emitted when a real-time tick or price update is received for a Ticker.
    """

    ticker: Ticker
    price: Price

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "ticker": self.ticker.to_dict(),
                "price": self.price.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PriceUpdatedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            ticker=Ticker.from_dict(data["ticker"]),
            price=Price.from_dict(data["price"]),
        )


@dataclass(frozen=True, kw_only=True)
class BarClosedEvent(DomainEvent):
    """
    Emitted when an OHLCV candle timeframe bar closes.
    """

    ticker: Ticker
    candle: Candle

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "ticker": self.ticker.to_dict(),
                "candle": self.candle.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BarClosedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            ticker=Ticker.from_dict(data["ticker"]),
            candle=Candle.from_dict(data["candle"]),
        )
