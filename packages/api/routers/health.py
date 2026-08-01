"""
Health & Platform Information Router.

Provides GET /, GET /health, GET /readiness, GET /liveness, and GET /version endpoints.
"""

from fastapi import APIRouter

from packages.api.schemas.response import (
    HealthResponse,
    RootResponse,
    VersionResponse,
)

router = APIRouter(tags=["Health & Status"])


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
