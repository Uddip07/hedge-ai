"""
Pydantic Data Models for Zerodha Broker Integration.

Defines structured schemas for profiles, holdings, positions, margins, orders, GTT rules, and market data.
"""

from typing import Any

from pydantic import BaseModel, Field


class BrokerProfileModel(BaseModel):
    """Zerodha User Profile data model."""

    user_id: str
    user_name: str
    email: str
    user_type: str = "individual"
    broker: str = "ZERODHA"
    exchanges: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    order_types: list[str] = Field(default_factory=list)
    avatar_url: str | None = None


class BrokerHoldingModel(BaseModel):
    """Zerodha CNC Equity Holding model."""

    tradingsymbol: str
    exchange: str = "NSE"
    instrument_token: int = 0
    isin: str = ""
    quantity: int = 0
    t1_quantity: int = 0
    realised_quantity: int = 0
    authorised_quantity: int = 0
    opening_quantity: int = 0
    collateral_quantity: int = 0
    collateral_type: str = ""
    discrepancy: bool = False
    average_price: float = 0.0
    last_price: float = 0.0
    close_price: float = 0.0
    pnl: float = 0.0
    day_change: float = 0.0
    day_change_percentage: float = 0.0


class BrokerPositionModel(BaseModel):
    """Zerodha Net or Day Position model."""

    tradingsymbol: str
    exchange: str = "NSE"
    instrument_token: int = 0
    product: str = "CNC"  # CNC, MIS, NRML
    quantity: int = 0
    overnight_quantity: int = 0
    multiplier: int = 1
    average_price: float = 0.0
    close_price: float = 0.0
    last_price: float = 0.0
    value: float = 0.0
    pnl: float = 0.0
    m2m: float = 0.0
    unrealised: float = 0.0
    realised: float = 0.0
    buy_quantity: int = 0
    buy_price: float = 0.0
    buy_value: float = 0.0
    buy_m2m: float = 0.0
    sell_quantity: int = 0
    sell_price: float = 0.0
    sell_value: float = 0.0
    sell_m2m: float = 0.0
    day_buy_quantity: int = 0
    day_buy_price: float = 0.0
    day_buy_value: float = 0.0
    day_sell_quantity: int = 0
    day_sell_price: float = 0.0
    day_sell_value: float = 0.0


class BrokerFundModel(BaseModel):
    """Zerodha Account Margins / Funds model."""

    net: float = 0.0
    available_cash: float = 0.0
    available_collateral: float = 0.0
    utilised_debits: float = 0.0
    utilised_span: float = 0.0
    utilised_option_premium: float = 0.0
    utilised_holding_sales: float = 0.0
    utilised_exposure: float = 0.0
    segment: str = "equity"


class BrokerOrderModel(BaseModel):
    """Zerodha Order model."""

    order_id: str
    exchange_order_id: str | None = None
    parent_order_id: str | None = None
    status: str
    status_message: str | None = None
    tradingsymbol: str
    exchange: str = "NSE"
    transaction_type: str  # BUY or SELL
    order_type: str  # MARKET, LIMIT, SL, SL-M
    product: str  # CNC, MIS, NRML
    validity: str = "DAY"
    quantity: int = 0
    filled_quantity: int = 0
    pending_quantity: int = 0
    price: float = 0.0
    trigger_price: float = 0.0
    average_price: float = 0.0
    order_timestamp: str = ""
    exchange_timestamp: str | None = None
    tag: str | None = None


class GTTOrderModel(BaseModel):
    """Zerodha Good-Till-Triggered (GTT) model."""

    id: int
    user_id: str
    type: str  # single or two-leg
    status: str  # active, triggered, cancelled, expired
    condition: dict[str, Any] = Field(default_factory=dict)
    orders: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
