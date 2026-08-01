"""
Unit tests verifying Application Port interface abstractions and dummy implementations.
"""

import unittest
from decimal import Decimal
from typing import Any

from packages.application.ports import (
    BrokerPort,
    LLMPort,
    MarketDataPort,
    NotificationPort,
    PortfolioPort,
    ResearchPort,
    StoragePort,
)
from packages.domain.brokerage.execution import Execution
from packages.domain.brokerage.order import Order
from packages.domain.enums.market import ExchangeType, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, OrderId
from packages.domain.value_objects.temporal.timestamps import Timestamp


class DummyMarketDataPort(MarketDataPort):
    def get_latest_price(self, ticker: Ticker) -> Price:
        return Price.from_amount("2500.00")

    def get_historical_candles(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> list[Candle]:
        return []

    def get_company_profile(self, ticker: Ticker) -> Company | None:
        return None

    def is_market_open(self, exchange: ExchangeType) -> bool:
        return True


class DummyBrokerPort(BrokerPort):
    def login(self) -> str:
        return "http://localhost/login"

    def profile(self) -> dict[str, Any]:
        return {"user_id": "dummy"}

    def holdings(self) -> list[dict[str, Any]]:
        return []

    def positions(self) -> dict[str, Any]:
        return {"net": [], "day": []}

    def funds(self) -> dict[str, Any]:
        return {"equity": {"net": 100000.0}}

    def orders(self) -> list[dict[str, Any]]:
        return []

    def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        return {"order_id": "dummy_123"}

    def cancel_order_by_id(self, order_id: str, variety: str = "regular") -> dict[str, Any]:
        return {"order_id": order_id}

    def modify_order(
        self, order_id: str, order_data: dict[str, Any], variety: str = "regular"
    ) -> dict[str, Any]:
        return {"order_id": order_id}

    def gtt(self) -> list[dict[str, Any]]:
        return []

    def place_gtt(self, gtt_data: dict[str, Any]) -> dict[str, Any]:
        return {"trigger_id": 123}

    def quote(self, instruments: list[str]) -> dict[str, Any]:
        return {}

    def historical(
        self, instrument_token: int, timeframe: str, from_date: str, to_date: str
    ) -> list[dict[str, Any]]:
        return []

    def get_account_balance(self, broker_account_id: BrokerId) -> Money:
        return Money(Decimal("100000.00"))

    def submit_order(self, order: Order) -> Execution:
        return Execution(
            order_id=order.id,
            ticker=order.ticker,
            trade_type=order.trade_type,
            quantity=order.quantity,
            price=order.price or Price.from_amount("2500.00"),
            fee=Money(Decimal("10.00")),
            executed_at=Timestamp.now_utc(),
        )

    def cancel_order(self, order_id: OrderId) -> bool:
        return True

    def get_order_status(self, order_id: OrderId) -> Order | None:
        return None


class DummyStoragePort(StoragePort):
    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def store_file(
        self, file_path: str, content: bytes, content_type: str = "application/octet-stream"
    ) -> str:
        self._store[file_path] = content
        return file_path

    def retrieve_file(self, file_id: str) -> bytes:
        return self._store[file_id]

    def delete_file(self, file_id: str) -> bool:
        if file_id in self._store:
            del self._store[file_id]
            return True
        return False

    def exists(self, file_id: str) -> bool:
        return file_id in self._store


class TestPortsInterfaces(unittest.TestCase):
    def test_abstract_ports_cannot_be_instantiated(self) -> None:
        abstract_ports = [
            MarketDataPort,
            ResearchPort,
            PortfolioPort,
            BrokerPort,
            NotificationPort,
            LLMPort,
            StoragePort,
        ]
        for port_cls in abstract_ports:
            with self.subTest(port_cls=port_cls.__name__):
                with self.assertRaises(TypeError):
                    port_cls()

    def test_dummy_market_data_port(self) -> None:
        port = DummyMarketDataPort()
        t = Ticker("RELIANCE.NSE")
        p = port.get_latest_price(t)
        self.assertEqual(p.money.amount, Decimal("2500.00"))
        self.assertTrue(port.is_market_open(ExchangeType.NSE))

    def test_dummy_broker_port(self) -> None:
        port = DummyBrokerPort()
        b_id = BrokerId.generate()
        bal = port.get_account_balance(b_id)
        self.assertEqual(bal.amount, Decimal("100000.00"))
        self.assertTrue(port.cancel_order(OrderId.generate()))

    def test_dummy_storage_port(self) -> None:
        port = DummyStoragePort()
        key = port.store_file("reports/reliance.txt", b"Research Content")
        self.assertEqual(key, "reports/reliance.txt")
        self.assertTrue(port.exists("reports/reliance.txt"))
        self.assertEqual(port.retrieve_file("reports/reliance.txt"), b"Research Content")
        self.assertTrue(port.delete_file("reports/reliance.txt"))
        self.assertFalse(port.exists("reports/reliance.txt"))


if __name__ == "__main__":
    unittest.main()
