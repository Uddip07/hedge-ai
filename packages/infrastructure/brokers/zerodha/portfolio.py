"""
Zerodha Portfolio Manager Module.

Fetches and structures broker user profiles, long-term holdings, net/day positions,
and account margins/funds.
"""

import logging
from typing import Any

from packages.infrastructure.brokers.zerodha.client import ZerodhaClient
from packages.infrastructure.brokers.zerodha.models import (
    BrokerFundModel,
    BrokerHoldingModel,
    BrokerPositionModel,
    BrokerProfileModel,
)

logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.portfolio")


class ZerodhaPortfolioManager:
    """
    Portfolio, holdings, positions, and funds management component.
    """

    def __init__(self, client: ZerodhaClient) -> None:
        self.client = client

    def get_profile(self) -> dict[str, Any]:
        """Fetch logged-in user profile from Zerodha."""
        raw = self.client.profile()
        model = BrokerProfileModel(
            user_id=raw.get("user_id", ""),
            user_name=raw.get("user_name", raw.get("user_id", "")),
            email=raw.get("email", ""),
            user_type=raw.get("user_type", "individual"),
            broker=raw.get("broker", "ZERODHA"),
            exchanges=raw.get("exchanges", []),
            products=raw.get("products", []),
            order_types=raw.get("order_types", []),
            avatar_url=raw.get("avatar_url"),
        )
        return model.model_dump()

    def get_holdings(self) -> list[dict[str, Any]]:
        """Fetch CNC equity holdings."""
        raw_list = self.client.holdings()
        holdings: list[dict[str, Any]] = []

        for raw in raw_list:
            model = BrokerHoldingModel(
                tradingsymbol=raw.get("tradingsymbol", ""),
                exchange=raw.get("exchange", "NSE"),
                instrument_token=raw.get("instrument_token", 0),
                isin=raw.get("isin", ""),
                quantity=raw.get("quantity", 0),
                t1_quantity=raw.get("t1_quantity", 0),
                realised_quantity=raw.get("realised_quantity", 0),
                authorised_quantity=raw.get("authorised_quantity", 0),
                opening_quantity=raw.get("opening_quantity", 0),
                collateral_quantity=raw.get("collateral_quantity", 0),
                collateral_type=raw.get("collateral_type", ""),
                discrepancy=raw.get("discrepancy", False),
                average_price=float(raw.get("average_price", 0.0)),
                last_price=float(raw.get("last_price", 0.0)),
                close_price=float(raw.get("close_price", 0.0)),
                pnl=float(raw.get("pnl", 0.0)),
                day_change=float(raw.get("day_change", 0.0)),
                day_change_percentage=float(raw.get("day_change_percentage", 0.0)),
            )
            holdings.append(model.model_dump())

        return holdings

    def get_positions(self) -> dict[str, Any]:
        """Fetch net and day positions."""
        raw = self.client.positions()
        net_raw = raw.get("net", []) if isinstance(raw, dict) else []
        day_raw = raw.get("day", []) if isinstance(raw, dict) else []

        def _map(pos_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
            res = []
            for item in pos_list:
                model = BrokerPositionModel(
                    tradingsymbol=item.get("tradingsymbol", ""),
                    exchange=item.get("exchange", "NSE"),
                    instrument_token=item.get("instrument_token", 0),
                    product=item.get("product", "CNC"),
                    quantity=item.get("quantity", 0),
                    overnight_quantity=item.get("overnight_quantity", 0),
                    multiplier=item.get("multiplier", 1),
                    average_price=float(item.get("average_price", 0.0)),
                    close_price=float(item.get("close_price", 0.0)),
                    last_price=float(item.get("last_price", 0.0)),
                    value=float(item.get("value", 0.0)),
                    pnl=float(item.get("pnl", 0.0)),
                    m2m=float(item.get("m2m", 0.0)),
                    unrealised=float(item.get("unrealised", 0.0)),
                    realised=float(item.get("realised", 0.0)),
                    buy_quantity=item.get("buy_quantity", 0),
                    buy_price=float(item.get("buy_price", 0.0)),
                    buy_value=float(item.get("buy_value", 0.0)),
                    sell_quantity=item.get("sell_quantity", 0),
                    sell_price=float(item.get("sell_price", 0.0)),
                    sell_value=float(item.get("sell_value", 0.0)),
                )
                res.append(model.model_dump())
            return res

        return {
            "net": _map(net_raw),
            "day": _map(day_raw),
        }

    def get_funds(self) -> dict[str, Any]:
        """Fetch account cash balances and margin utilization for equity."""
        raw = self.client.margins(segment="equity")
        available = raw.get("available", {}) if isinstance(raw, dict) else {}
        utilised = raw.get("utilised", {}) if isinstance(raw, dict) else {}

        model = BrokerFundModel(
            net=float(raw.get("net", 0.0)) if isinstance(raw, dict) else 0.0,
            available_cash=float(available.get("live_balance", available.get("cash", 0.0))),
            available_collateral=float(available.get("collateral", 0.0)),
            utilised_debits=float(utilised.get("debits", 0.0)),
            utilised_span=float(utilised.get("span", 0.0)),
            utilised_option_premium=float(utilised.get("option_premium", 0.0)),
            utilised_holding_sales=float(utilised.get("holding_sales", 0.0)),
            utilised_exposure=float(utilised.get("exposure", 0.0)),
            segment="equity",
        )
        return model.model_dump()
