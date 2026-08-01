"""
Zerodha KiteConnect Official SDK Infrastructure Package.

Exports adapter, authenticator, token store, client, websocket ticker, portfolio,
orders, GTT managers, and data models for Zerodha integration.
"""

from packages.infrastructure.brokers.zerodha.adapter import ZerodhaBrokerAdapter
from packages.infrastructure.brokers.zerodha.alert_service import (
    AlertRule,
    ZerodhaAlertService,
)
from packages.infrastructure.brokers.zerodha.auth import (
    FileTokenStore,
    TokenStore,
    ZerodhaAuthenticator,
    ZerodhaAuthenticator as ZerodhaAuthService,
)
from packages.infrastructure.brokers.zerodha.client import (
    ZerodhaClient,
    ZerodhaError,
    ZerodhaMarginError,
    ZerodhaMarketDataForbiddenError,
    ZerodhaOrderError,
    ZerodhaTokenError,
)
from packages.infrastructure.brokers.zerodha.gtt import (
    ZerodhaGTTManager,
    ZerodhaGTTManager as ZerodhaGTTService,
)
from packages.infrastructure.brokers.zerodha.models import (
    BrokerFundModel,
    BrokerHoldingModel,
    BrokerOrderModel,
    BrokerPositionModel,
    BrokerProfileModel,
    GTTOrderModel,
)
from packages.infrastructure.brokers.zerodha.orders import (
    ZerodhaOrderManager,
    ZerodhaOrderManager as ZerodhaOrderService,
)
from packages.infrastructure.brokers.zerodha.portfolio import (
    ZerodhaPortfolioManager,
    ZerodhaPortfolioManager as ZerodhaPortfolioService,
)


class ZerodhaMarginService:
    def __init__(self, client: ZerodhaClient) -> None:
        self.client = client

    def get_equity_available_cash(self) -> float:
        res = self.client.margins(segment="equity")
        available = res.get("available", {}) if isinstance(res, dict) else {}
        return float(available.get("live_balance", available.get("cash", 0.0)))


__all__ = [
    "ZerodhaBrokerAdapter",
    "ZerodhaAuthenticator",
    "ZerodhaAuthService",
    "TokenStore",
    "FileTokenStore",
    "ZerodhaClient",
    "ZerodhaWebSocket",
    "ZerodhaPortfolioManager",
    "ZerodhaPortfolioService",
    "ZerodhaOrderManager",
    "ZerodhaOrderService",
    "ZerodhaGTTManager",
    "ZerodhaGTTService",
    "ZerodhaMarginService",
    "ZerodhaAlertService",
    "AlertRule",
    "BrokerProfileModel",
    "BrokerHoldingModel",
    "BrokerPositionModel",
    "BrokerFundModel",
    "BrokerOrderModel",
    "GTTOrderModel",
    "ZerodhaError",
    "ZerodhaTokenError",
    "ZerodhaOrderError",
    "ZerodhaMarginError",
    "ZerodhaMarketDataForbiddenError",
]
