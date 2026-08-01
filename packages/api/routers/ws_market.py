"""
FastAPI WebSocket Router for Live Market Data Streaming.

Provides real-time price updates, market depth ticker streaming, heartbeat ping/pong,
and ticker subscription support over WebSockets for the Indian AI Hedge Fund platform.
"""

import asyncio
import json
import random
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from packages.infrastructure.logging import get_logger

logger = get_logger(name="ihf_ai.api.ws_market")

router = APIRouter(tags=["Market Data Stream"])


# Active WebSocket connection manager
class ConnectionManager:
    """Manages active WebSocket client connections and broadcasting."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket client disconnected. Total active: {len(self.active_connections)}"
            )

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket) -> None:
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict[str, Any]) -> None:
        payload = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as exc:
                logger.warning(f"Error broadcasting to WebSocket client: {exc}")
                self.disconnect(connection)


manager = ConnectionManager()

# Default Indian Market Tickers
INITIAL_TICKERS: list[dict[str, Any]] = [
    {
        "ticker": "NIFTY.NSE",
        "name": "NIFTY 50",
        "price": 24350.50,
        "change": 125.40,
        "change_percent": 0.52,
        "volume": 25045000,
        "high": 24420.00,
        "low": 24210.00,
    },
    {
        "ticker": "BANKNIFTY.NSE",
        "name": "NIFTY BANK",
        "price": 52180.20,
        "change": -180.30,
        "change_percent": -0.34,
        "volume": 18200000,
        "high": 52500.00,
        "low": 52050.00,
    },
    {
        "ticker": "RELIANCE.NSE",
        "name": "Reliance Industries",
        "price": 2980.45,
        "change": 32.10,
        "change_percent": 1.09,
        "volume": 8420000,
        "high": 2995.00,
        "low": 2950.00,
    },
    {
        "ticker": "TCS.NSE",
        "name": "Tata Consultancy Services",
        "price": 4250.80,
        "change": -15.20,
        "change_percent": -0.36,
        "volume": 3120000,
        "high": 4280.00,
        "low": 4230.00,
    },
    {
        "ticker": "INFY.NSE",
        "name": "Infosys Ltd",
        "price": 1820.60,
        "change": 14.50,
        "change_percent": 0.80,
        "volume": 5900000,
        "high": 1835.00,
        "low": 1805.00,
    },
    {
        "ticker": "HDFCBANK.NSE",
        "name": "HDFC Bank",
        "price": 1640.25,
        "change": 8.75,
        "change_percent": 0.54,
        "volume": 12400000,
        "high": 1652.00,
        "low": 1630.00,
    },
    {
        "ticker": "ICICIBANK.NSE",
        "name": "ICICI Bank",
        "price": 1215.10,
        "change": -4.30,
        "change_percent": -0.35,
        "volume": 9800000,
        "high": 1225.00,
        "low": 1208.00,
    },
    {
        "ticker": "SENSEX.BSE",
        "name": "BSE SENSEX",
        "price": 80120.75,
        "change": 410.20,
        "change_percent": 0.51,
        "volume": 45000000,
        "high": 80350.00,
        "low": 79800.00,
    },
]


@router.websocket("/ws/market-data")
async def websocket_market_data_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket streaming endpoint for real-time market quotes and ticker updates.
    """
    await manager.connect(websocket)

    # State copy per connection
    ticker_state: dict[str, dict[str, Any]] = {
        item["ticker"]: dict(item) for item in INITIAL_TICKERS
    }

    # Send initial snapshot
    await manager.send_personal_message(
        {
            "type": "SNAPSHOT",
            "timestamp": datetime.now(UTC).isoformat(),
            "data": list(ticker_state.values()),
        },
        websocket,
    )

    # Spawn background simulator task for this connection
    async def stream_live_updates() -> None:
        while True:
            await asyncio.sleep(1.5)
            # Pick a random ticker to update
            target_ticker = random.choice(list(ticker_state.keys()))
            item = ticker_state[target_ticker]

            # Price delta (-0.4% to +0.4%)
            delta_pct = random.uniform(-0.004, 0.004)
            old_price = float(item["price"])
            curr_change = float(item["change"])
            curr_high = float(item["high"])
            curr_low = float(item["low"])

            new_price = round(old_price * (1.0 + delta_pct), 2)
            price_change = round(new_price - old_price, 2)

            item["price"] = new_price
            item["change"] = round(curr_change + price_change, 2)
            item["change_percent"] = round(
                (item["change"] / (new_price - item["change"])) * 100.0, 2
            )
            item["high"] = max(curr_high, new_price)
            item["low"] = min(curr_low, new_price)

            direction = "up" if price_change > 0 else ("down" if price_change < 0 else "flat")

            update_msg = {
                "type": "TICK",
                "timestamp": datetime.now(UTC).isoformat(),
                "data": {
                    **item,
                    "price_change": price_change,
                    "direction": direction,
                },
            }
            await manager.send_personal_message(update_msg, websocket)

    updater_task = asyncio.create_task(stream_live_updates())

    try:
        while True:
            text = await websocket.receive_text()
            data = json.loads(text)
            msg_type = data.get("type")

            if msg_type == "PING":
                await manager.send_personal_message(
                    {"type": "PONG", "timestamp": datetime.now(UTC).isoformat()},
                    websocket,
                )
            elif msg_type == "SUBSCRIBE":
                requested = data.get("tickers", [])
                logger.info(f"Client requested subscription for {requested}")
                await manager.send_personal_message(
                    {
                        "type": "SUBSCRIBED",
                        "tickers": requested,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                    websocket,
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        updater_task.cancel()
    except Exception as exc:
        logger.error(f"WebSocket exception: {exc}")
        manager.disconnect(websocket)
        updater_task.cancel()
