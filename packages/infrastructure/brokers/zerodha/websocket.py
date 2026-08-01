"""
Zerodha KiteTicker WebSocket Streaming Wrapper.

Provides event-driven real-time streaming wrappers around official kiteconnect.KiteTicker SDK.
"""

import logging
import os
from collections.abc import Callable
from typing import Any

try:
    from kiteconnect import KiteTicker
except ImportError:

    class KiteTicker:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass


logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.websocket")


class ZerodhaWebSocket:
    """
    WebSocket streaming adapter encapsulating official KiteTicker instance.
    """

    def __init__(
        self,
        api_key: str | None = None,
        access_token: str | None = None,
        ticker_instance: KiteTicker | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("ZERODHA_API_KEY", "")
        self.access_token = access_token or os.getenv("ZERODHA_ACCESS_TOKEN", "")

        if ticker_instance:
            self.kws = ticker_instance
        else:
            self.kws = KiteTicker(api_key=self.api_key, access_token=self.access_token)

        self._tick_callbacks: list[Callable[[list[dict[str, Any]]], None]] = []
        self._connect_callbacks: list[Callable[[], None]] = []
        self._close_callbacks: list[Callable[[int, str], None]] = []
        self._error_callbacks: list[Callable[[int, str], None]] = []

        self._register_internal_handlers()

    def _register_internal_handlers(self) -> None:
        """Wire KiteTicker SDK internal callbacks to registered custom listeners."""

        def _on_ticks(ws: Any, ticks: list[dict[str, Any]]) -> None:
            logger.debug("Received %d websocket market ticks", len(ticks))
            for cb in self._tick_callbacks:
                try:
                    cb(ticks)
                except Exception as exc:
                    logger.error("Error in websocket tick callback: %s", str(exc))

        def _on_connect(ws: Any, response: Any) -> None:
            logger.info("Zerodha KiteTicker websocket connected successfully.")
            for cb in self._connect_callbacks:
                try:
                    cb()
                except Exception as exc:
                    logger.error("Error in websocket connect callback: %s", str(exc))

        def _on_close(ws: Any, code: int, reason: str) -> None:
            logger.warning("Zerodha KiteTicker websocket closed (code=%s, reason=%s)", code, reason)
            for cb in self._close_callbacks:
                try:
                    cb(code, reason)
                except Exception as exc:
                    logger.error("Error in websocket close callback: %s", str(exc))

        def _on_error(ws: Any, code: int, reason: str) -> None:
            logger.error("Zerodha KiteTicker websocket error (code=%s, reason=%s)", code, reason)
            for cb in self._error_callbacks:
                try:
                    cb(code, reason)
                except Exception as exc:
                    logger.error("Error in websocket error callback: %s", str(exc))

        self.kws.on_ticks = _on_ticks
        self.kws.on_connect = _on_connect
        self.kws.on_close = _on_close
        self.kws.on_error = _on_error

    def on_ticks(self, callback: Callable[[list[dict[str, Any]]], None]) -> None:
        """Register a callback for tick updates."""
        self._tick_callbacks.append(callback)

    def on_connect(self, callback: Callable[[], None]) -> None:
        """Register a callback for websocket connection established."""
        self._connect_callbacks.append(callback)

    def on_close(self, callback: Callable[[int, str], None]) -> None:
        """Register a callback for websocket connection closure."""
        self._close_callbacks.append(callback)

    def on_error(self, callback: Callable[[int, str], None]) -> None:
        """Register a callback for websocket errors."""
        self._error_callbacks.append(callback)

    def connect(self, threaded: bool = True) -> None:
        """Connect to Zerodha WebSocket ticker streaming server."""
        logger.info("Connecting Zerodha KiteTicker websocket...")
        self.kws.connect(threaded=threaded)

    def subscribe(self, instrument_tokens: list[int]) -> None:
        """Subscribe to streaming tick updates for given instrument tokens."""
        self.kws.subscribe(instrument_tokens)

    def unsubscribe(self, instrument_tokens: list[int]) -> None:
        """Unsubscribe from streaming tick updates for given instrument tokens."""
        self.kws.unsubscribe(instrument_tokens)

    def set_mode(self, mode: str, instrument_tokens: list[int]) -> None:
        """
        Set streaming mode ('full', 'quote', 'ltp') for given instrument tokens.
        """
        if mode == "full":
            self.kws.set_mode(self.kws.MODE_FULL, instrument_tokens)
        elif mode == "quote":
            self.kws.set_mode(self.kws.MODE_QUOTE, instrument_tokens)
        elif mode == "ltp":
            self.kws.set_mode(self.kws.MODE_LTP, instrument_tokens)

    def close(self) -> None:
        """Close the active websocket connection."""
        self.kws.close()
