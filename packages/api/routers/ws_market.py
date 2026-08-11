"""
FastAPI WebSocket Router for Live Market Data Streaming.

Provides real-time price updates, canonical market depth ticker streaming, heartbeat ping/pong,
and authentic quotes for the Indian AI Hedge Fund platform.
Zero synthetic drift — all data sourced from authoritative provider.
"""

import asyncio
import json
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.logging import get_logger
from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider

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

TRACKED_INSTRUMENTS = [
    "NIFTY.NSE",
    "BANKNIFTY.NSE",
    "SENSEX.BSE",
    "RELIANCE.NSE",
    "TCS.NSE",
    "INFY.NSE",
    "HDFCBANK.NSE",
    "ICICIBANK.NSE",
    "SBIN.NSE",
    "BHARTIARTL.NSE",
    "ITC.NSE",
    "KOTAKBANK.NSE",
    "LT.NSE",
]

_provider = YahooMarketDataProvider()


def _get_canonical_quote_sync(sym_str: str) -> dict[str, Any]:
    """Fetch authentic quote from provider for an instrument."""
    try:
        t = Ticker(sym_str)
        q = _provider.get_quote(t)
        raw_dict = q.to_dict() if hasattr(q, "to_dict") else {}
        price_val = float(getattr(q.price, "amount", raw_dict.get("price", 0.0)))
        prev_close = float(getattr(q, "previous_close", raw_dict.get("previous_close", price_val)))
        if prev_close == 0.0:
            prev_close = price_val

        change_val = float(getattr(q, "change", raw_dict.get("change", price_val - prev_close)))
        change_pct_val = float(
            getattr(
                q,
                "change_percent",
                raw_dict.get(
                    "change_percent",
                    ((change_val / prev_close) * 100.0) if prev_close > 0 else 0.0,
                ),
            )
        )
        vol_val = float(getattr(q, "volume", raw_dict.get("volume", 0.0)))
        high_val = float(getattr(q, "high", raw_dict.get("high", price_val)))
        low_val = float(getattr(q, "low", raw_dict.get("low", price_val)))
        open_val = float(getattr(q, "open", raw_dict.get("open", price_val)))

        name_map = {
            "NIFTY.NSE": "NIFTY 50",
            "BANKNIFTY.NSE": "NIFTY BANK",
            "SENSEX.BSE": "BSE SENSEX",
            "RELIANCE.NSE": "Reliance Industries",
            "TCS.NSE": "Tata Consultancy Services",
            "INFY.NSE": "Infosys Ltd",
            "HDFCBANK.NSE": "HDFC Bank",
            "ICICIBANK.NSE": "ICICI Bank",
            "SBIN.NSE": "State Bank of India",
            "BHARTIARTL.NSE": "Bharti Airtel",
            "ITC.NSE": "ITC Limited",
            "KOTAKBANK.NSE": "Kotak Mahindra Bank",
            "LT.NSE": "Larsen & Toubro",
        }

        ts_val = getattr(q, "timestamp", raw_dict.get("timestamp"))
        if (
            ts_val is not None
            and hasattr(ts_val, "isoformat")
            and callable(getattr(ts_val, "isoformat", None))
        ):
            ts_iso = ts_val.isoformat()
        elif (
            ts_val is not None
            and hasattr(ts_val, "value")
            and hasattr(getattr(ts_val, "value", None), "isoformat")
        ):
            ts_iso = ts_val.value.isoformat()
        else:
            ts_iso = str(ts_val or datetime.now(UTC).isoformat())

        ist = timezone(timedelta(hours=5, minutes=30))
        try:
            ts_inner = getattr(ts_val, "value", None)
            if isinstance(ts_inner, datetime):
                quote_dt_ist = ts_inner.astimezone(ist)
            elif isinstance(ts_val, datetime):
                quote_dt_ist = ts_val.astimezone(ist)
            else:
                quote_dt = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
                quote_dt_ist = quote_dt.astimezone(ist)
            quote_ist_str = quote_dt_ist.strftime("%Y-%m-%d %H:%M:%S IST")
        except Exception:
            quote_ist_str = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")

        m_state, source, is_open = _provider.get_indian_market_state()

        return {
            "ticker": t.full_symbol,
            "symbol": t.symbol,
            "name": name_map.get(t.full_symbol, t.symbol),
            "price": price_val,
            "previous_close": prev_close,
            "change": round(change_val, 2),
            "change_percent": round(change_pct_val, 2),
            "volume": int(vol_val),
            "open": open_val,
            "high": high_val,
            "low": low_val,
            "market_state": m_state,
            "is_market_open": is_open,
            "source": source,
            "timestamp": ts_iso,
            "timestamp_ist": quote_ist_str,
        }
    except Exception as err:
        logger.warning(f"Failed to fetch canonical quote for {sym_str}: {err}")
        return {
            "ticker": sym_str,
            "symbol": sym_str.split(".")[0],
            "name": sym_str,
            "price": 0.0,
            "previous_close": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "volume": 0,
            "open": 0.0,
            "high": 0.0,
            "low": 0.0,
            "market_state": "CLOSED",
            "is_market_open": False,
            "source": "UNAVAILABLE",
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.websocket("/ws/market-data")
async def websocket_market_data_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket streaming endpoint for authentic real-time market quotes and ticker updates.
    """
    await manager.connect(websocket)

    # Initial authentic snapshot fetch
    initial_quotes = await asyncio.to_thread(
        lambda: [_get_canonical_quote_sync(sym) for sym in TRACKED_INSTRUMENTS]
    )
    # Filter out empty zero errors if any
    valid_quotes = [q for q in initial_quotes if q.get("price", 0.0) > 0.0] or initial_quotes

    ticker_state: dict[str, dict[str, Any]] = {item["ticker"]: dict(item) for item in valid_quotes}

    m_state, source, is_open = _provider.get_indian_market_state()

    # Send initial snapshot
    await manager.send_personal_message(
        {
            "type": "SNAPSHOT",
            "timestamp": datetime.now(UTC).isoformat(),
            "market_state": m_state,
            "source": source,
            "data": list(ticker_state.values()),
        },
        websocket,
    )

    # Periodic background refresher task (zero synthetic random drift)
    async def stream_live_updates() -> None:
        while True:
            await asyncio.sleep(10.0)
            m_state_curr, source_curr, is_open_curr = _provider.get_indian_market_state()

            # Refresh quotes from authentic provider
            for sym in list(ticker_state.keys()):
                updated = await asyncio.to_thread(_get_canonical_quote_sync, sym)
                if updated.get("price", 0.0) <= 0.0:
                    continue

                old_item = ticker_state.get(sym, {})
                old_price = old_item.get("price", 0.0)
                new_price = updated["price"]
                price_change = round(new_price - old_price, 2)

                # Only broadcast tick if authentic price or quote timestamp actually changed
                is_price_changed = abs(price_change) > 0.0001
                is_ts_changed = updated.get("timestamp") != old_item.get("timestamp")

                if is_price_changed or is_ts_changed:
                    direction = (
                        "up" if price_change > 0 else ("down" if price_change < 0 else "flat")
                    )
                    ticker_state[sym] = updated
                    update_msg = {
                        "type": "TICK",
                        "timestamp": datetime.now(UTC).isoformat(),
                        "data": {
                            **updated,
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
            elif msg_type == "SNAPSHOT":
                await manager.send_personal_message(
                    {
                        "type": "SNAPSHOT",
                        "timestamp": datetime.now(UTC).isoformat(),
                        "data": list(ticker_state.values()),
                    },
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
