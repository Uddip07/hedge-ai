"""
API Routers Package.

Exports health_router, analyze_router, market_router, company_intelligence_router, and committee_router.
"""

from packages.api.routers.alert import router as alert_router
from packages.api.routers.analyze import router as analyze_router
from packages.api.routers.auth import router as auth_router
from packages.api.routers.backtest import router as backtest_router
from packages.api.routers.broker import router as broker_router
from packages.api.routers.committee import router as committee_router
from packages.api.routers.company_intelligence import (
    router as company_intelligence_router,
)
from packages.api.routers.debug import router as debug_router
from packages.api.routers.health import router as health_router
from packages.api.routers.market import router as market_router
from packages.api.routers.market_data import router as market_data_router
from packages.api.routers.user import router as user_router
from packages.api.routers.ws_market import router as ws_market_router

__all__ = [
    "alert_router",
    "analyze_router",
    "auth_router",
    "backtest_router",
    "broker_router",
    "committee_router",
    "company_intelligence_router",
    "debug_router",
    "health_router",
    "market_router",
    "market_data_router",
    "user_router",
    "ws_market_router",
]
