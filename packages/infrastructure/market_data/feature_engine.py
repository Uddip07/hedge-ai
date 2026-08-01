"""
Quantitative Feature Engine Infrastructure.

Provides feature storage, versioning, retrieval, and indicator calculations
for technical and quantitative features (EMA, SMA, MACD, RSI, ADX, ATR, VWAP,
Returns, Log Returns, Momentum, Volatility).
"""

import math
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import and_, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from packages.infrastructure.database.models import (
    FeatureCacheModel,
)


@dataclass
class FeatureRecord:
    """Quantitative feature record DTO."""

    company_id: str
    date: date
    feature_name: str
    feature_value: float
    feature_version: str = "v1.0"


class FeatureEngine:
    """
    Feature Store Infrastructure Manager.
    """

    def __init__(self, session_factory: Callable[..., Any]) -> None:
        self.session_factory = session_factory

    def save_features(self, records: list[FeatureRecord]) -> int:
        """
        Persist or update calculated feature records in feature_cache table.
        """
        if not records:
            return 0

        data = [
            {
                "id": str(uuid.uuid4()),
                "company_id": r.company_id,
                "date": r.date,
                "feature_name": r.feature_name,
                "feature_value": float(r.feature_value),
                "feature_version": r.feature_version,
                "created_at": datetime.now(UTC),
            }
            for r in records
        ]

        with self.session_factory() as session:
            try:
                dialect = session.bind.dialect.name if session.bind else "sqlite"
                stmt: Any = None
                if dialect == "postgresql":
                    pg_stmt = pg_insert(FeatureCacheModel).values(data)
                    stmt = pg_stmt.on_conflict_do_update(
                        index_elements=["company_id", "date", "feature_name", "feature_version"],
                        set_={"feature_value": pg_stmt.excluded.feature_value},
                    )
                elif dialect == "sqlite":
                    sqlite_stmt = sqlite_insert(FeatureCacheModel).values(data)
                    stmt = sqlite_stmt.on_conflict_do_update(
                        index_elements=["company_id", "date", "feature_name", "feature_version"],
                        set_={"feature_value": sqlite_stmt.excluded.feature_value},
                    )
                else:
                    stmt = insert(FeatureCacheModel).values(data)

                session.execute(stmt)
                session.commit()
                return len(records)
            except Exception:
                session.rollback()
                saved = 0
                for d in data:
                    try:
                        session.execute(insert(FeatureCacheModel).values(d))
                        session.commit()
                        saved += 1
                    except Exception:
                        session.rollback()
                return saved

    def get_features(
        self,
        company_id: str,
        target_date: date,
        feature_names: list[str] | None = None,
        feature_version: str = "v1.0",
    ) -> dict[str, float]:
        """
        Retrieve feature vector for a company on a given date.
        """
        with self.session_factory() as session:
            query = select(FeatureCacheModel).where(
                and_(
                    FeatureCacheModel.company_id == company_id,
                    FeatureCacheModel.date == target_date,
                    FeatureCacheModel.feature_version == feature_version,
                )
            )

            if feature_names:
                query = query.where(FeatureCacheModel.feature_name.in_(feature_names))

            results = session.execute(query).scalars().all()
            return {r.feature_name: r.feature_value for r in results}

    def compute_basic_returns(self, prices: list[float]) -> list[float]:
        """Compute simple percentage returns series."""
        if len(prices) < 2:
            return []
        returns = []
        for i in range(1, len(prices)):
            prev = prices[i - 1]
            curr = prices[i]
            ret = (curr - prev) / prev if prev != 0 else 0.0
            returns.append(ret)
        return returns

    def compute_log_returns(self, prices: list[float]) -> list[float]:
        """Compute logarithmic returns series."""
        if len(prices) < 2:
            return []
        log_ret = []
        for i in range(1, len(prices)):
            prev = prices[i - 1]
            curr = prices[i]
            if prev > 0 and curr > 0:
                log_ret.append(math.log(curr / prev))
            else:
                log_ret.append(0.0)
        return log_ret

    def compute_sma(self, prices: list[float], window: int) -> float | None:
        """Compute Simple Moving Average of trailing window."""
        if len(prices) < window:
            return None
        return sum(prices[-window:]) / window

    def compute_ema(self, prices: list[float], window: int) -> float | None:
        """Compute Exponential Moving Average."""
        if len(prices) < window:
            return None
        k = 2.0 / (window + 1)
        ema = sum(prices[:window]) / window
        for price in prices[window:]:
            ema = (price * k) + (ema * (1 - k))
        return ema
