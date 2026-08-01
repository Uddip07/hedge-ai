"""
Broker API Router for Infrastructure Layer.

Exposes REST endpoints for user broker profile, holdings, positions, funds, order book,
order placement, and GTT trigger management depending on BrokerPort interface.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from packages.api.dependencies import get_broker_port
from packages.application.ports.broker_port import BrokerPort

router = APIRouter(prefix="/broker", tags=["Broker Gateway"])


class PlaceOrderRequest(BaseModel):
    """Order placement request payload."""

    tradingsymbol: str
    exchange: str = "NSE"
    transaction_type: str = "BUY"  # BUY or SELL
    order_type: str = "LIMIT"  # MARKET, LIMIT, SL, SL-M
    product: str = "CNC"  # CNC, MIS, NRML
    quantity: int = Field(gt=0)
    price: float | None = None
    trigger_price: float | None = None
    variety: str = "regular"
    validity: str = "DAY"
    tag: str = "moneyyyyyy"


class PlaceGTTRequest(BaseModel):
    """GTT placement request payload."""

    trigger_type: str = "single"  # single or two-leg
    tradingsymbol: str
    exchange: str = "NSE"
    trigger_values: list[float]
    last_price: float
    orders: list[dict[str, Any]]


@router.get("/profile")
async def get_profile(broker_port: BrokerPort = Depends(get_broker_port)) -> dict[str, Any]:
    """
    Get authenticated broker profile details.
    """
    try:
        return broker_port.profile()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch broker profile: {exc}",
        ) from exc


@router.get("/holdings")
async def get_holdings(broker_port: BrokerPort = Depends(get_broker_port)) -> list[dict[str, Any]]:
    """
    Get long-term CNC equity holdings.
    """
    try:
        return broker_port.holdings()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch holdings: {exc}",
        ) from exc


@router.get("/positions")
async def get_positions(broker_port: BrokerPort = Depends(get_broker_port)) -> dict[str, Any]:
    """
    Get net and day trading positions.
    """
    try:
        return broker_port.positions()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch positions: {exc}",
        ) from exc


@router.get("/funds")
async def get_funds(broker_port: BrokerPort = Depends(get_broker_port)) -> dict[str, Any]:
    """
    Get cash balances and margin utilization.
    """
    try:
        return broker_port.funds()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch funds: {exc}",
        ) from exc


@router.get("/orders")
async def get_orders(broker_port: BrokerPort = Depends(get_broker_port)) -> list[dict[str, Any]]:
    """
    Get order book for the current trading session.
    """
    try:
        return broker_port.orders()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {exc}",
        ) from exc


@router.post("/order")
async def place_order(
    payload: PlaceOrderRequest,
    broker_port: BrokerPort = Depends(get_broker_port),
) -> dict[str, Any]:
    """
    Place a new trading order.
    """
    try:
        return broker_port.place_order(payload.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order placement failed: {exc}",
        ) from exc


@router.post("/gtt")
async def place_gtt(
    payload: PlaceGTTRequest,
    broker_port: BrokerPort = Depends(get_broker_port),
) -> dict[str, Any]:
    """
    Create a new Good-Till-Triggered (GTT) rule.
    """
    try:
        return broker_port.place_gtt(payload.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GTT creation failed: {exc}",
        ) from exc
