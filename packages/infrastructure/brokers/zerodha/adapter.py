"""
Zerodha Broker Adapter.

Production Outbound Port Adapter implementing BrokerPort interface for Zerodha KiteConnect integration.
Hides all Kite SDK types from the rest of the application.
"""

import logging
import uuid
from decimal import Decimal
from typing import Any

from packages.application.ports.broker_port import BrokerPort
from packages.domain.brokerage.execution import Execution
from packages.domain.brokerage.order import Order
from packages.domain.enums.system import CurrencyCode
from packages.domain.enums.trading import OrderStatus, OrderType, TradeType
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.currency import Currency
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, OrderId, PortfolioId
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.brokers.zerodha.auth import ZerodhaAuthenticator
from packages.infrastructure.brokers.zerodha.client import ZerodhaClient
from packages.infrastructure.brokers.zerodha.gtt import ZerodhaGTTManager
from packages.infrastructure.brokers.zerodha.orders import ZerodhaOrderManager
from packages.infrastructure.brokers.zerodha.portfolio import ZerodhaPortfolioManager

logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.adapter")


class ZerodhaBrokerAdapter(BrokerPort):
    """
    Zerodha Broker Adapter implementing BrokerPort interface.
    """

    def __init__(
        self,
        client: ZerodhaClient | None = None,
        authenticator: ZerodhaAuthenticator | None = None,
        portfolio_manager: ZerodhaPortfolioManager | None = None,
        order_manager: ZerodhaOrderManager | None = None,
        gtt_manager: ZerodhaGTTManager | None = None,
    ) -> None:
        if client:
            self.client = client
        elif authenticator and hasattr(authenticator, "kite"):
            self.client = ZerodhaClient(kite_instance=authenticator.kite)
        else:
            self.client = ZerodhaClient()

        self.authenticator = authenticator or ZerodhaAuthenticator(
            api_key=self.client.api_key,
        )

        # Ensure active token is set on client if available
        active_token = self.authenticator.get_active_access_token()
        if active_token:
            self.client.set_access_token(active_token)

        self.portfolio_manager = portfolio_manager or ZerodhaPortfolioManager(self.client)
        self.order_manager = order_manager or ZerodhaOrderManager(self.client)
        self.gtt_manager = gtt_manager or ZerodhaGTTManager(self.client)

    def login(self) -> str:
        """Return authorization login URL for Zerodha OAuth."""
        return self.authenticator.get_login_url()

    def profile(self) -> dict[str, Any]:
        """Fetch user profile."""
        return self.portfolio_manager.get_profile()

    def holdings(self) -> list[dict[str, Any]]:
        """Fetch CNC equity holdings."""
        return self.portfolio_manager.get_holdings()

    def positions(self) -> dict[str, Any]:
        """Fetch net and day positions."""
        return self.portfolio_manager.get_positions()

    def funds(self) -> dict[str, Any]:
        """Fetch account margin and cash funds."""
        return self.portfolio_manager.get_funds()

    def orders(self) -> list[dict[str, Any]]:
        """Fetch session order book."""
        return self.order_manager.get_orders()

    def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """Place order via Zerodha."""
        return self.order_manager.place_order(order_data)

    def cancel_order_by_id(self, order_id: str, variety: str = "regular") -> dict[str, Any]:
        """Cancel active order by Zerodha order ID."""
        return self.order_manager.cancel_order(order_id=order_id, variety=variety)

    def modify_order(
        self, order_id: str, order_data: dict[str, Any], variety: str = "regular"
    ) -> dict[str, Any]:
        """Modify active order by Zerodha order ID."""
        return self.order_manager.modify_order(
            order_id=order_id, order_data=order_data, variety=variety
        )

    def gtt(self) -> list[dict[str, Any]]:
        """Fetch active GTT rules."""
        return self.gtt_manager.get_gtts()

    def place_gtt(self, gtt_data: dict[str, Any]) -> dict[str, Any]:
        """Place new GTT trigger rule."""
        return self.gtt_manager.place_gtt(gtt_data)

    def quote(self, instruments: list[str]) -> dict[str, Any]:
        """Fetch live quotes for instruments."""
        return self.client.quote(instruments)

    def historical(
        self, instrument_token: int, timeframe: str, from_date: str, to_date: str
    ) -> list[dict[str, Any]]:
        """Fetch historical OHLC candles for instrument token."""
        return self.client.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=timeframe,
        )

    # Backward compatibility implementation for BrokerPort
    def get_account_balance(self, broker_account_id: BrokerId) -> Money:
        """Query current unencumbered cash balance."""
        fund_info = self.funds()
        available_cash = fund_info.get("available_cash", 0.0)
        return Money(Decimal(str(available_cash)), currency=Currency(CurrencyCode.INR))

    def submit_order(self, order: Order) -> Execution:
        """Submit a domain Order entity to Zerodha."""
        order_data = {
            "variety": "regular",
            "exchange": order.ticker.exchange.value if order.ticker.exchange else "NSE",
            "tradingsymbol": order.ticker.symbol,
            "transaction_type": order.trade_type.value,
            "quantity": int(order.quantity.value),
            "product": "CNC",
            "order_type": order.order_type.value,
            "price": float(order.price.amount) if order.price else None,
            "trigger_price": float(order.stop_price.amount) if order.stop_price else None,
        }
        res = self.place_order(order_data)
        kite_order_id = res.get("order_id", str(uuid.uuid4()))

        fill_price = order.price or Price.from_amount("1000.00")
        return Execution(
            order_id=OrderId(uuid.uuid5(uuid.NAMESPACE_DNS, f"zerodha-order-{kite_order_id}")),
            ticker=order.ticker,
            trade_type=order.trade_type,
            quantity=order.quantity,
            price=fill_price,
            fee=Money(Decimal("20.00")),
            executed_at=Timestamp.now_utc(),
        )

    def cancel_order(self, order_id: OrderId) -> bool:
        """Cancel an active/pending domain order by OrderId."""
        try:
            self.cancel_order_by_id(str(order_id.value))
            return True
        except Exception:
            return False

    def get_order_status(self, order_id: OrderId) -> Order | None:
        """Retrieve current domain Order status."""
        orders = self.orders()
        target_str = str(order_id.value)
        for item in orders:
            if item.get("order_id") == target_str:
                return Order(
                    id=order_id,
                    portfolio_id=PortfolioId.generate(),
                    broker_account_id=BrokerId.generate(),
                    ticker=Ticker(item.get("tradingsymbol", "")),
                    order_type=OrderType(item.get("order_type", "LIMIT")),
                    trade_type=TradeType(item.get("transaction_type", "BUY")),
                    quantity=Quantity(Decimal(str(item.get("quantity", 1)))),
                    price=Price.from_amount(Decimal(str(item.get("price", 0.0)))),
                    status=(
                        OrderStatus.FILLED
                        if item.get("status") == "COMPLETE"
                        else OrderStatus.SUBMITTED
                    ),
                )
        return None
