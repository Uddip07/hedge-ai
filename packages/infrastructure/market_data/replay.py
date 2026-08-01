"""
Market Replay Engine for Time-Travel Simulation & Backtesting.

Enforces zero future leakage: strictly queries price records with date <= target_date.
Supports single stock, full market snapshot, index, and sector replay.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import and_, func, select

from packages.infrastructure.database.models import (
    CompanyModel,
    MarketIndexModel,
    PriceHistoryDailyModel,
)


@dataclass
class MarketReplayCandle:
    """
    Standardized replay candle DTO returned to backtester / simulation engine.
    """

    company_id: str
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float | None
    volume: int
    vwap: float | None


class MarketReplayService:
    """
    Market Replay Service guaranteeing point-in-time accuracy without lookahead bias.
    """

    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    def get_stock_replay(
        self, symbol: str, target_date: date, lookback_candles: int = 100
    ) -> list[MarketReplayCandle]:
        """
        Get price history for a single stock strictly UP TO target_date (date <= target_date).
        """
        clean_sym = symbol.strip().upper()

        with self.session_factory() as session:
            stmt = (
                select(PriceHistoryDailyModel, CompanyModel.symbol)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .where(
                    and_(
                        CompanyModel.symbol == clean_sym,
                        PriceHistoryDailyModel.date <= target_date,
                    )
                )
                .order_by(PriceHistoryDailyModel.date.desc())
                .limit(lookback_candles)
            )

            results = session.execute(stmt).all()

            # Return in chronological order (oldest to newest)
            candles = [
                MarketReplayCandle(
                    company_id=row.PriceHistoryDailyModel.company_id,
                    symbol=row.symbol,
                    date=row.PriceHistoryDailyModel.date,
                    open=row.PriceHistoryDailyModel.open,
                    high=row.PriceHistoryDailyModel.high,
                    low=row.PriceHistoryDailyModel.low,
                    close=row.PriceHistoryDailyModel.close,
                    adjusted_close=row.PriceHistoryDailyModel.adjusted_close,
                    volume=row.PriceHistoryDailyModel.volume,
                    vwap=row.PriceHistoryDailyModel.vwap,
                )
                for row in reversed(results)
            ]

            return candles

    def get_market_snapshot(self, target_date: date) -> list[MarketReplayCandle]:
        """
        Get latest available closing candle for ALL active companies as of target_date.
        """
        with self.session_factory() as session:
            # Subquery for max date per company on or before target_date
            subq = (
                select(
                    PriceHistoryDailyModel.company_id,
                    func.max(PriceHistoryDailyModel.date).label("max_date"),
                )
                .where(PriceHistoryDailyModel.date <= target_date)
                .group_by(PriceHistoryDailyModel.company_id)
                .subquery()
            )

            stmt = (
                select(PriceHistoryDailyModel, CompanyModel.symbol)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .join(
                    subq,
                    and_(
                        PriceHistoryDailyModel.company_id == subq.c.company_id,
                        PriceHistoryDailyModel.date == subq.c.max_date,
                    ),
                )
                .order_by(CompanyModel.symbol.asc())
            )

            results = session.execute(stmt).all()

            return [
                MarketReplayCandle(
                    company_id=row.PriceHistoryDailyModel.company_id,
                    symbol=row.symbol,
                    date=row.PriceHistoryDailyModel.date,
                    open=row.PriceHistoryDailyModel.open,
                    high=row.PriceHistoryDailyModel.high,
                    low=row.PriceHistoryDailyModel.low,
                    close=row.PriceHistoryDailyModel.close,
                    adjusted_close=row.PriceHistoryDailyModel.adjusted_close,
                    volume=row.PriceHistoryDailyModel.volume,
                    vwap=row.PriceHistoryDailyModel.vwap,
                )
                for row in results
            ]

    def get_sector_replay(
        self, sector: str, target_date: date, lookback_candles: int = 30
    ) -> list[MarketReplayCandle]:
        """
        Get price history for all stocks in a specific sector up to target_date.
        """
        with self.session_factory() as session:
            stmt = (
                select(PriceHistoryDailyModel, CompanyModel.symbol)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .where(
                    and_(
                        CompanyModel.sector.ilike(f"%{sector}%"),
                        PriceHistoryDailyModel.date <= target_date,
                    )
                )
                .order_by(PriceHistoryDailyModel.date.asc())
            )

            results = session.execute(stmt).all()

            return [
                MarketReplayCandle(
                    company_id=row.PriceHistoryDailyModel.company_id,
                    symbol=row.symbol,
                    date=row.PriceHistoryDailyModel.date,
                    open=row.PriceHistoryDailyModel.open,
                    high=row.PriceHistoryDailyModel.high,
                    low=row.PriceHistoryDailyModel.low,
                    close=row.PriceHistoryDailyModel.close,
                    adjusted_close=row.PriceHistoryDailyModel.adjusted_close,
                    volume=row.PriceHistoryDailyModel.volume,
                    vwap=row.PriceHistoryDailyModel.vwap,
                )
                for row in results
            ]

    def get_index_replay(
        self, index_symbol: str, target_date: date, lookback_candles: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get index historical performance up to target_date.
        """
        clean_sym = index_symbol.strip().upper()

        with self.session_factory() as session:
            stmt = (
                select(MarketIndexModel)
                .where(
                    and_(
                        MarketIndexModel.symbol == clean_sym,
                        MarketIndexModel.date <= target_date,
                    )
                )
                .order_by(MarketIndexModel.date.desc())
                .limit(lookback_candles)
            )

            results = session.execute(stmt).scalars().all()

            return [
                {
                    "symbol": r.symbol,
                    "name": r.name,
                    "date": r.date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": r.volume,
                    "change": r.change,
                    "pct_change": r.pct_change,
                }
                for r in reversed(results)
            ]
