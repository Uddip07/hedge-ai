"""
SQL Market Data Repository Implementation.

Provides clean architecture repository methods for querying historical prices,
rolling windows, market snapshots, sector feeds, index feeds, and company metadata.
"""

from datetime import date
from typing import Any

from sqlalchemy import and_, func, select

from packages.domain.repositories.price_history_repository import PriceHistoryRepository
from packages.infrastructure.database.models import (
    CompanyModel,
    PriceHistoryDailyModel,
)


class SQLMarketDataRepository(PriceHistoryRepository):
    """
    SQLAlchemy 2.x Repository for Market Data access.
    """

    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    def get_company_history(
        self, symbol: str, start_date: date | None = None, end_date: date | None = None
    ) -> list[dict[str, Any]]:
        """Load full or range-filtered company daily price records."""
        clean_sym = symbol.strip().upper()

        with self.session_factory() as session:
            stmt = (
                select(PriceHistoryDailyModel)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .where(CompanyModel.symbol == clean_sym)
            )

            if start_date:
                stmt = stmt.where(PriceHistoryDailyModel.date >= start_date)
            if end_date:
                stmt = stmt.where(PriceHistoryDailyModel.date <= end_date)

            stmt = stmt.order_by(PriceHistoryDailyModel.date.asc())
            rows = session.execute(stmt).scalars().all()

            return [
                {
                    "date": r.date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "adjusted_close": r.adjusted_close,
                    "volume": r.volume,
                    "vwap": r.vwap,
                    "delivery_quantity": r.delivery_quantity,
                    "turnover": r.turnover,
                }
                for r in rows
            ]

    def get_rolling_window(
        self, symbol: str, end_date: date, window_days: int
    ) -> list[dict[str, Any]]:
        """Load trailing window of historical candles as of end_date."""
        clean_sym = symbol.strip().upper()

        with self.session_factory() as session:
            stmt = (
                select(PriceHistoryDailyModel)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .where(
                    and_(
                        CompanyModel.symbol == clean_sym,
                        PriceHistoryDailyModel.date <= end_date,
                    )
                )
                .order_by(PriceHistoryDailyModel.date.desc())
                .limit(window_days)
            )

            rows = session.execute(stmt).scalars().all()
            return [
                {
                    "date": r.date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": r.volume,
                    "vwap": r.vwap,
                }
                for r in reversed(rows)
            ]

    def get_previous_n_candles(self, symbol: str, end_date: date, n: int) -> list[dict[str, Any]]:
        """Load previous N candles strictly on or prior to end_date."""
        return self.get_rolling_window(symbol, end_date, n)

    def get_market_snapshot(self, as_of_date: date) -> list[dict[str, Any]]:
        """Load latest closing price across all companies as of date."""
        with self.session_factory() as session:
            subq = (
                select(
                    PriceHistoryDailyModel.company_id,
                    func.max(PriceHistoryDailyModel.date).label("max_date"),
                )
                .where(PriceHistoryDailyModel.date <= as_of_date)
                .group_by(PriceHistoryDailyModel.company_id)
                .subquery()
            )

            stmt = (
                select(PriceHistoryDailyModel, CompanyModel)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .join(
                    subq,
                    and_(
                        PriceHistoryDailyModel.company_id == subq.c.company_id,
                        PriceHistoryDailyModel.date == subq.c.max_date,
                    ),
                )
            )

            results = session.execute(stmt).all()
            return [
                {
                    "symbol": row.CompanyModel.symbol,
                    "company_name": row.CompanyModel.company_name,
                    "sector": row.CompanyModel.sector,
                    "date": row.PriceHistoryDailyModel.date,
                    "open": row.PriceHistoryDailyModel.open,
                    "high": row.PriceHistoryDailyModel.high,
                    "low": row.PriceHistoryDailyModel.low,
                    "close": row.PriceHistoryDailyModel.close,
                    "volume": row.PriceHistoryDailyModel.volume,
                }
                for row in results
            ]

    def get_sector_history(
        self, sector: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        """Load sector history across all constituent companies."""
        with self.session_factory() as session:
            stmt = (
                select(PriceHistoryDailyModel, CompanyModel.symbol)
                .join(CompanyModel, PriceHistoryDailyModel.company_id == CompanyModel.id)
                .where(
                    and_(
                        CompanyModel.sector.ilike(f"%{sector}%"),
                        PriceHistoryDailyModel.date >= start_date,
                        PriceHistoryDailyModel.date <= end_date,
                    )
                )
                .order_by(PriceHistoryDailyModel.date.asc())
            )

            results = session.execute(stmt).all()
            return [
                {
                    "symbol": row.symbol,
                    "date": row.PriceHistoryDailyModel.date,
                    "close": row.PriceHistoryDailyModel.close,
                    "volume": row.PriceHistoryDailyModel.volume,
                }
                for row in results
            ]
