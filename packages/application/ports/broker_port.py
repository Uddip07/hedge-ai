"""
Broker Port Interface for the Application Layer.

Defines abstract outbound port contracts for authentication, account profiles,
portfolio holdings/positions, funds, order management, GTT rules, and market data queries.
"""

from abc import ABC, abstractmethod
from typing import Any

from packages.domain.brokerage.execution import Execution
from packages.domain.brokerage.order import Order
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, OrderId


class BrokerPort(ABC):
    """
    Abstract Outbound Port for Exchange Broker Integration (Zerodha/Upstox/AngelOne/etc.).
    """

    @abstractmethod
    def login(self) -> str:
        """Return authorization login URL for OAuth authentication."""

    @abstractmethod
    def profile(self) -> dict[str, Any]:
        """Fetch authenticated user profile details from broker."""

    @abstractmethod
    def holdings(self) -> list[dict[str, Any]]:
        """Fetch long-term portfolio equity holdings."""

    @abstractmethod
    def positions(self) -> dict[str, Any]:
        """Fetch net and day positions."""

    @abstractmethod
    def funds(self) -> dict[str, Any]:
        """Fetch fund balances and margin limits."""

    @abstractmethod
    def orders(self) -> list[dict[str, Any]]:
        """Fetch list of orders placed in the current session."""

    @abstractmethod
    def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """Place a new trading order with broker gateway."""

    @abstractmethod
    def cancel_order_by_id(self, order_id: str, variety: str = "regular") -> dict[str, Any]:
        """Cancel an active order by broker order ID."""

    @abstractmethod
    def modify_order(
        self, order_id: str, order_data: dict[str, Any], variety: str = "regular"
    ) -> dict[str, Any]:
        """Modify an active order by broker order ID."""

    @abstractmethod
    def gtt(self) -> list[dict[str, Any]]:
        """Fetch Good-Till-Triggered (GTT) rules."""

    @abstractmethod
    def place_gtt(self, gtt_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new Good-Till-Triggered (GTT) rule."""

    @abstractmethod
    def quote(self, instruments: list[str]) -> dict[str, Any]:
        """Fetch live market quote feeds for given instrument keys."""

    @abstractmethod
    def historical(
        self, instrument_token: int, timeframe: str, from_date: str, to_date: str
    ) -> list[dict[str, Any]]:
        """Fetch historical OHLCV data candles."""

    # Backward compatibility methods
    @abstractmethod
    def get_account_balance(self, broker_account_id: BrokerId) -> Money:
        """Query current unencumbered cash balance for a broker account."""

    @abstractmethod
    def submit_order(self, order: Order) -> Execution:
        """Submit a new domain Order entity to execution gateway."""

    @abstractmethod
    def cancel_order(self, order_id: OrderId) -> bool:
        """Cancel an active/pending order by domain OrderId."""

    @abstractmethod
    def get_order_status(self, order_id: OrderId) -> Order | None:
        """Retrieve current domain Order entity status."""
