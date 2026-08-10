import os
import time
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from sqlalchemy import func, select, text

from packages.api.schemas.response import (
    HealthResponse,
    RootResponse,
    VersionResponse,
)
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.database.models import PriceHistoryDailyModel
from packages.infrastructure.database.session import DatabaseManager
from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider

router = APIRouter(tags=["Health & Status"])
db_manager = DatabaseManager()


@router.get(
    "/",
    response_model=RootResponse,
    summary="Root Status",
    description="Get top-level application identity and running status.",
)
async def get_root() -> RootResponse:
    """Return root platform status payload."""
    return RootResponse(
        application="MONEYYYYYY",
        version="1.0.0",
        status="running",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Get platform component health status.",
)
async def get_health() -> HealthResponse:
    """Return platform subsystem health check status."""
    return HealthResponse(
        status="healthy",
        database="configured",
        cache="configured",
        application="running",
    )


@router.get(
    "/health/detailed",
    summary="Detailed Subsystem Health & Connectivity Check",
    description="Performs live non-mocked connectivity and freshness checks across PostgreSQL, Redis, Yahoo Finance, and Market Data.",
)
async def get_health_detailed() -> dict[str, Any]:
    """Return comprehensive live health metrics for orchestration monitoring."""
    checks: dict[str, Any] = {}
    overall_healthy = True

    # 1. Database Check (Live Query)
    db_start = time.perf_counter()
    try:
        with db_manager.session() as session:
            session.execute(text("SELECT 1"))
            db_latency = round((time.perf_counter() - db_start) * 1000, 2)
            checks["database"] = {
                "status": "healthy",
                "latency_ms": db_latency,
                "message": "Database query executed successfully",
            }
    except Exception as exc:
        overall_healthy = False
        checks["database"] = {
            "status": "unhealthy",
            "latency_ms": round((time.perf_counter() - db_start) * 1000, 2),
            "error": str(exc),
        }

    # 2. Redis Cache Check
    redis_url = os.getenv("REDIS_URL")
    cache_enabled = os.getenv("CACHE_ENABLED", "false").lower() in ("true", "1", "yes")
    if cache_enabled and redis_url:
        try:
            import redis

            r = redis.from_url(redis_url, socket_timeout=2)
            r_start = time.perf_counter()
            r.ping()
            r_latency = round((time.perf_counter() - r_start) * 1000, 2)
            checks["redis"] = {
                "status": "healthy",
                "latency_ms": r_latency,
                "configured": True,
            }
        except Exception as r_exc:
            checks["redis"] = {
                "status": "degraded",
                "configured": True,
                "error": str(r_exc),
            }
    else:
        checks["redis"] = {
            "status": "disabled",
            "configured": False,
            "message": "Redis cache is not enabled",
        }

    # 3. Yahoo Finance Live Provider Check
    yf_start = time.perf_counter()
    try:
        provider = YahooMarketDataProvider()
        quote = provider.get_quote(Ticker("RELIANCE.NSE"))
        yf_latency = round((time.perf_counter() - yf_start) * 1000, 2)
        checks["yahoo_provider"] = {
            "status": "healthy",
            "latency_ms": yf_latency,
            "sample_ticker": "RELIANCE.NSE",
            "last_price": str(quote.price.amount),
            "timestamp": quote.timestamp.isoformat(),
        }
    except Exception as exc:
        checks["yahoo_provider"] = {
            "status": "degraded",
            "latency_ms": round((time.perf_counter() - yf_start) * 1000, 2),
            "error": str(exc),
        }

    # 4. Market Data Freshness in Database
    try:
        with db_manager.session() as session:
            latest_price_date = session.scalar(select(func.max(PriceHistoryDailyModel.date)))
            total_records = session.scalar(select(func.count(PriceHistoryDailyModel.id))) or 0
            checks["data_freshness"] = {
                "latest_price_date": str(latest_price_date) if latest_price_date else None,
                "total_records": total_records,
                "status": "active" if total_records > 0 else "empty",
            }
    except Exception as exc:
        checks["data_freshness"] = {
            "status": "error",
            "error": str(exc),
        }

    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "components": checks,
    }


@router.get(
    "/readiness",
    response_model=HealthResponse,
    summary="Readiness Check",
    description="Indicate whether the API is ready to serve traffic.",
)
async def get_readiness() -> HealthResponse:
    """Return readiness status for deployment probes."""
    return HealthResponse(
        status="ready",
        database="configured",
        cache="configured",
        application="running",
    )


@router.get(
    "/liveness",
    response_model=HealthResponse,
    summary="Liveness Check",
    description="Indicate whether the API process is alive.",
)
async def get_liveness() -> HealthResponse:
    """Return liveness status for deployment probes."""
    return HealthResponse(
        status="alive",
        database="configured",
        cache="configured",
        application="running",
    )


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Version Information",
    description="Get platform software version metadata.",
)
async def get_version() -> VersionResponse:
    """Return software version and build metadata."""
    return VersionResponse()
