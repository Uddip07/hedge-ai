"""
Zerodha Good-Till-Triggered (GTT) Manager Module.

Handles placing, listing, modifying, and deleting GTT trigger rules.
"""

import logging
from typing import Any

from packages.infrastructure.brokers.zerodha.client import ZerodhaClient
from packages.infrastructure.brokers.zerodha.models import GTTOrderModel

logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.gtt")


class ZerodhaGTTManager:
    """
    GTT rule management component.
    """

    def __init__(self, client: ZerodhaClient) -> None:
        self.client = client

    def get_gtts(self) -> list[dict[str, Any]]:
        """Fetch active GTT rules."""
        raw_list = self.client.get_gtts()
        gtts: list[dict[str, Any]] = []

        for raw in raw_list:
            model = GTTOrderModel(
                id=int(raw.get("id", 0)),
                user_id=str(raw.get("user_id", "")),
                type=raw.get("type", "single"),
                status=raw.get("status", "active"),
                condition=raw.get("condition", {}),
                orders=raw.get("orders", []),
                created_at=str(raw.get("created_at", "")),
                updated_at=str(raw.get("updated_at", "")),
            )
            gtts.append(model.model_dump())

        return gtts

    def place_gtt(self, gtt_data: dict[str, Any]) -> dict[str, Any]:
        """
        Place a new GTT trigger rule.

        Requires gtt_data dict containing:
        trigger_type ('single' or 'two-leg'), tradingsymbol, exchange, trigger_values, last_price, orders.
        """
        trigger_type = gtt_data.get("trigger_type", "single")
        tradingsymbol = gtt_data.get("tradingsymbol", "").replace(".NS", "").replace(".BO", "")
        exchange = gtt_data.get("exchange", "NSE")
        trigger_values = [float(v) for v in gtt_data.get("trigger_values", [])]
        last_price = float(gtt_data.get("last_price", 0.0))
        orders = gtt_data.get("orders", [])

        res = self.client.place_gtt(
            trigger_type=trigger_type,
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            trigger_values=trigger_values,
            last_price=last_price,
            orders=orders,
        )
        return res
