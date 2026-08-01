"""
Mock Broker Adapter for Infrastructure Layer.

Simulates broker order placement, execution fills, and account balance queries.
Zero live broker API connectivity (DhanHQ/Shoonya/Zerodha/IB).
"""

from decimal import Decimal
from typing import Any

from packages.application.ports.broker_port import BrokerPort
from packages.domain.brokerage.execution import Execution
from packages.domain.brokerage.order import Order
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, OrderId
from packages.domain.value_objects.temporal.timestamps import Timestamp


class MockBrokerAdapter(BrokerPort):
    """
    Mock Adapter implementing BrokerPort for local backtest and simulation.
    """

    def __init__(self) -> None:
        self._balances: dict[str, Money] = {}
        self._orders: dict[str, Order] = {}

    def login(self) -> str:
        return "http://localhost/auth/zerodha/login"

    def profile(self) -> dict[str, Any]:
        return {"user_id": "MOCK_USER", "user_name": "Mock User", "email": "mock@example.com"}

    def holdings(self) -> list[dict[str, Any]]:
        return []

    def positions(self) -> dict[str, Any]:
        return {"net": [], "day": []}

    def funds(self) -> dict[str, Any]:
        return {"equity": {"net": 1000000.0, "available": 1000000.0}}

    def orders(self) -> list[dict[str, Any]]:
        return []

    def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        return {"order_id": "MOCK_ORDER_123", "status": "COMPLETE"}

    def cancel_order_by_id(self, order_id: str, variety: str = "regular") -> dict[str, Any]:
        return {"order_id": order_id, "status": "CANCELLED"}

    def modify_order(
        self, order_id: str, order_data: dict[str, Any], variety: str = "regular"
    ) -> dict[str, Any]:
        return {"order_id": order_id, "status": "MODIFIED"}

    def gtt(self) -> list[dict[str, Any]]:
        return []

    def place_gtt(self, gtt_data: dict[str, Any]) -> dict[str, Any]:
        return {"trigger_id": 12345, "status": "active"}

    def quote(self, instruments: list[str]) -> dict[str, Any]:
        return {inst: {"last_price": 1000.0} for inst in instruments}

    def historical(
        self, instrument_token: int, timeframe: str, from_date: str, to_date: str
    ) -> list[dict[str, Any]]:
        return []

    def get_account_balance(self, broker_account_id: BrokerId) -> Money:
        key = str(broker_account_id.value)
        return self._balances.get(key, Money(Decimal("1000000.00")))

    def submit_order(self, order: Order) -> Execution:
        key = str(order.id.value)
        self._orders[key] = order

        fill_price = order.price or Price.from_amount("1000.00")
        return Execution(
            order_id=order.id,
            ticker=order.ticker,
            trade_type=order.trade_type,
            quantity=order.quantity,
            price=fill_price,
            fee=Money(Decimal("20.00")),
            executed_at=Timestamp.now_utc(),
        )

    def cancel_order(self, order_id: OrderId) -> bool:
        key = str(order_id.value)
        if key in self._orders:
            del self._orders[key]
            return True
        return False

    def get_order_status(self, order_id: OrderId) -> Order | None:
        key = str(order_id.value)
        return self._orders.get(key)
