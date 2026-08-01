"""
Market Data Mapper for Infrastructure Layer.

Translates between raw market data structures / provider DTOs and domain value objects.
"""

from decimal import Decimal
from typing import Any

from packages.domain.enums.market import MarketSegment, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import OHLCV, Candle
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.models import MarketQuote


class MarketDataMapper:
    """
    Bidirectional mapper converting between raw provider structures and domain models.
    """

    @staticmethod
    def to_market_quote(
        ticker: Ticker,
        price_amount: Decimal | float | str,
        change_24h: Decimal | float | str = "0.00",
        volume_24h: Decimal | float | str = "0.00",
    ) -> MarketQuote:
        """Construct MarketQuote model from primitive inputs."""
        p = Price.from_amount(Decimal(str(price_amount)))
        return MarketQuote(
            ticker=ticker,
            price=p,
            change_24h=Decimal(str(change_24h)),
            volume_24h=Decimal(str(volume_24h)),
            timestamp=Timestamp.now_utc(),
        )

    @staticmethod
    def to_candle(
        timestamp: Timestamp,
        timeframe: Timeframe,
        open_price: Decimal | float | str,
        high_price: Decimal | float | str,
        low_price: Decimal | float | str,
        close_price: Decimal | float | str,
        volume: Decimal | float | str,
    ) -> Candle:
        """Construct Candle domain object from raw bar components."""
        ohlcv = OHLCV(
            open=Price.from_amount(Decimal(str(open_price))),
            high=Price.from_amount(Decimal(str(high_price))),
            low=Price.from_amount(Decimal(str(low_price))),
            close=Price.from_amount(Decimal(str(close_price))),
            volume=Quantity(Decimal(str(volume))),
        )
        return Candle(timestamp=timestamp, timeframe=timeframe, ohlcv=ohlcv)

    @staticmethod
    def to_company_profile(
        name: str,
        sector: MarketSegment | str = MarketSegment.LARGE_CAP,
        industry: str = "Financial Services",
        metadata: dict[str, Any] | None = None,
    ) -> Company:
        """Construct Company domain object."""
        sec = sector if isinstance(sector, MarketSegment) else MarketSegment(sector)
        return Company(
            name=name,
            sector=sec,
            industry=industry,
        )
