"""
Broker API Router for Infrastructure Layer.

Exposes REST endpoints for user broker profile, holdings, positions, funds, order book,
order placement, and GTT trigger management depending on BrokerPort interface.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from packages.api.dependencies import get_broker_port, verify_automation_key
from packages.application.ports.broker_port import BrokerPort
from packages.infrastructure.logging import get_logger

logger = get_logger(name="ihf_ai.api.routers.broker")

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
        logger.error(f"Failed to fetch broker profile: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch broker profile. Broker service unreachable or unauthenticated.",
        ) from None


@router.get("/holdings")
async def get_holdings(broker_port: BrokerPort = Depends(get_broker_port)) -> list[dict[str, Any]]:
    """
    Get long-term CNC equity holdings.
    """
    try:
        return broker_port.holdings()
    except Exception as exc:
        logger.error(f"Failed to fetch holdings: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch portfolio holdings from broker.",
        ) from None


@router.get("/positions")
async def get_positions(broker_port: BrokerPort = Depends(get_broker_port)) -> dict[str, Any]:
    """
    Get net and day trading positions.
    """
    try:
        return broker_port.positions()
    except Exception as exc:
        logger.error(f"Failed to fetch positions: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trading positions from broker.",
        ) from None


@router.get("/funds")
async def get_funds(broker_port: BrokerPort = Depends(get_broker_port)) -> dict[str, Any]:
    """
    Get cash balances and margin utilization.
    """
    try:
        return broker_port.funds()
    except Exception as exc:
        logger.error(f"Failed to fetch funds: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available margin and funds from broker.",
        ) from None


@router.get("/orders")
async def get_orders(broker_port: BrokerPort = Depends(get_broker_port)) -> list[dict[str, Any]]:
    """
    Get order book for the current trading session.
    """
    try:
        return broker_port.orders()
    except Exception as exc:
        logger.error(f"Failed to fetch orders: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order book from broker.",
        ) from None


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
        logger.error(f"Order placement failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order placement rejected by broker or exchange risk check.",
        ) from None


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
        logger.error(f"GTT creation failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GTT rule creation rejected by broker gateway.",
        ) from None


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_automation_key)],
    summary="Broker Gateway Health & Session Monitor",
    description="Check broker authentication, API connection, order book status, and rejected orders without exposing secrets or placing trades.",
)
async def get_broker_health(
    broker_port: BrokerPort = Depends(get_broker_port),
) -> dict[str, Any]:
    """
    Monitor Zerodha / Broker connection health, session validity, and order rejection events.
    """
    import time

    start_time = time.perf_counter()

    is_authenticated = False
    broker_type = getattr(broker_port, "provider_name", type(broker_port).__name__)
    profile_summary: dict[str, Any] = {}
    total_orders = 0
    open_orders = 0
    complete_orders = 0
    rejected_orders = 0
    cancelled_orders = 0
    recent_rejections: list[dict[str, Any]] = []
    error_detail: str | None = None

    try:
        # Check profile/authentication
        prof = broker_port.profile()
        is_authenticated = True
        profile_summary = {
            "user_id": prof.get("user_id", "authenticated"),
            "user_name": prof.get("user_name", "Broker User"),
            "broker": prof.get("broker", "Zerodha"),
        }
    except Exception as exc:
        logger.error(f"Broker health check session error: {exc}", exc_info=True)
        error_detail = "Broker session unauthenticated or connection error"

    if is_authenticated:
        try:
            orders = broker_port.orders() or []
            total_orders = len(orders)
            for o in orders:
                status_str = str(o.get("status", "")).upper()
                if status_str in ("OPEN", "TRIGGER PENDING"):
                    open_orders += 1
                elif status_str in ("COMPLETE",):
                    complete_orders += 1
                elif status_str in ("REJECTED",):
                    rejected_orders += 1
                    recent_rejections.append(
                        {
                            "order_id": o.get("order_id"),
                            "tradingsymbol": o.get("tradingsymbol"),
                            "transaction_type": o.get("transaction_type"),
                            "status_message": o.get("status_message")
                            or o.get("rejection_reason", "Rejected by exchange/RMS"),
                            "order_timestamp": o.get("order_timestamp"),
                        }
                    )
                elif status_str in ("CANCELLED",):
                    cancelled_orders += 1
        except Exception:
            pass

    order_stats: dict[str, Any] = {
        "total_orders": total_orders,
        "open_orders": open_orders,
        "complete_orders": complete_orders,
        "rejected_orders": rejected_orders,
        "cancelled_orders": cancelled_orders,
        "recent_rejections": recent_rejections,
    }

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "status": "HEALTHY" if is_authenticated else "DEGRADED",
        "broker_type": broker_type,
        "is_authenticated": is_authenticated,
        "latency_ms": latency_ms,
        "profile": profile_summary,
        "orders_summary": order_stats,
        "error": error_detail,
    }
