"""
Zerodha Order Management Component.

Handles order submission, modification, cancellation, and order history queries.
"""

import logging
from typing import Any

from packages.infrastructure.brokers.zerodha.client import ZerodhaClient
from packages.infrastructure.brokers.zerodha.models import BrokerOrderModel

logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.orders")


class ZerodhaOrderManager:
    """
    Order execution and management component.
    """

    def __init__(self, client: ZerodhaClient) -> None:
        self.client = client

    def get_orders(self) -> list[dict[str, Any]]:
        """Fetch session order book."""
        raw_list = self.client.orders()
        orders: list[dict[str, Any]] = []

        for raw in raw_list:
            model = BrokerOrderModel(
                order_id=str(raw.get("order_id", "")),
                exchange_order_id=raw.get("exchange_order_id"),
                parent_order_id=raw.get("parent_order_id"),
                status=raw.get("status", "PENDING"),
                status_message=raw.get("status_message"),
                tradingsymbol=raw.get("tradingsymbol", ""),
                exchange=raw.get("exchange", "NSE"),
                transaction_type=raw.get("transaction_type", "BUY"),
                order_type=raw.get("order_type", "LIMIT"),
                product=raw.get("product", "CNC"),
                validity=raw.get("validity", "DAY"),
                quantity=raw.get("quantity", 0),
                filled_quantity=raw.get("filled_quantity", 0),
                pending_quantity=raw.get("pending_quantity", 0),
                price=float(raw.get("price", 0.0)),
                trigger_price=float(raw.get("trigger_price", 0.0)),
                average_price=float(raw.get("average_price", 0.0)),
                order_timestamp=str(raw.get("order_timestamp", "")),
                exchange_timestamp=raw.get("exchange_timestamp"),
                tag=raw.get("tag"),
            )
            orders.append(model.model_dump())

        return orders

    def place_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """
        Place a new order with Zerodha.

        Requires order_data dict containing:
        variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price, trigger_price.
        """
        variety = order_data.get("variety", "regular")
        exchange = order_data.get("exchange", "NSE")
        tradingsymbol = order_data.get("tradingsymbol", "").replace(".NS", "").replace(".BO", "")
        transaction_type = order_data.get("transaction_type", "BUY").upper()
        quantity = int(order_data.get("quantity", 1))
        product = order_data.get("product", "CNC").upper()
        order_type = order_data.get("order_type", "LIMIT").upper()
        price = (
            float(order_data["price"])
            if "price" in order_data and order_data["price"] is not None
            else None
        )
        trigger_price = (
            float(order_data["trigger_price"])
            if "trigger_price" in order_data and order_data["trigger_price"] is not None
            else None
        )
        validity = order_data.get("validity", "DAY")
        tag = order_data.get("tag", "moneyyyyyy")

        order_id = self.client.place_order(
            variety=variety,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            transaction_type=transaction_type,
            quantity=quantity,
            product=product,
            order_type=order_type,
            price=price,
            trigger_price=trigger_price,
            validity=validity,
            tag=tag,
        )

        return {
            "order_id": order_id,
            "status": "SUBMITTED",
            "tradingsymbol": tradingsymbol,
            "exchange": exchange,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": price,
            "product": product,
            "order_type": order_type,
        }

    def modify_order(
        self, order_id: str, order_data: dict[str, Any], variety: str = "regular"
    ) -> dict[str, Any]:
        """Modify an active order."""
        quantity = (
            int(order_data["quantity"])
            if "quantity" in order_data and order_data["quantity"] is not None
            else None
        )
        price = (
            float(order_data["price"])
            if "price" in order_data and order_data["price"] is not None
            else None
        )
        trigger_price = (
            float(order_data["trigger_price"])
            if "trigger_price" in order_data and order_data["trigger_price"] is not None
            else None
        )
        order_type = order_data.get("order_type")
        validity = order_data.get("validity")

        res_id = self.client.modify_order(
            variety=variety,
            order_id=order_id,
            quantity=quantity,
            price=price,
            trigger_price=trigger_price,
            order_type=order_type,
            validity=validity,
        )
        return {"order_id": res_id, "status": "MODIFIED"}

    def cancel_order(self, order_id: str, variety: str = "regular") -> dict[str, Any]:
        """Cancel an active order."""
        res_id = self.client.cancel_order(variety=variety, order_id=order_id)
        return {"order_id": res_id, "status": "CANCELLED"}
