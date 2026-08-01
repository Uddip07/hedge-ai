"""
Zerodha Client Wrapper using official kiteconnect SDK.

Provides high-level error handling, rate-limit management, exception mapping,
and execution wrapping over official KiteConnect APIs.
"""

import logging
import os
import time
from typing import Any, cast

try:
    from kiteconnect import KiteConnect
    from kiteconnect.exceptions import (
        DataException,
        InputException,
        KiteException,
        NetworkException,
        OrderException,
        PermissionException,
        TokenException,
    )
except ImportError:

    class KiteException(Exception):  # type: ignore[no-redef]
        pass

    class DataException(KiteException):  # type: ignore[misc,no-redef]
        pass

    class InputException(KiteException):  # type: ignore[misc,no-redef]
        pass

    class NetworkException(KiteException):  # type: ignore[misc,no-redef]
        pass

    class OrderException(KiteException):  # type: ignore[misc,no-redef]
        pass

    class PermissionException(KiteException):  # type: ignore[misc,no-redef]
        pass

    class TokenException(KiteException):  # type: ignore[misc,no-redef]
        pass

    class KiteConnect:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass


logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.client")


class ZerodhaError(Exception):
    """Base exception for Zerodha integration errors."""


class ZerodhaTokenError(ZerodhaError, PermissionError):
    """Raised when Zerodha session token is invalid or expired."""


class ZerodhaOrderError(ZerodhaError, ValueError):
    """Raised when Zerodha order placement or modification fails."""


class ZerodhaMarginError(ZerodhaError, ValueError):
    """Raised when Zerodha margin or fund checks fail."""


class ZerodhaMarketDataForbiddenError(ZerodhaError, PermissionError):
    """Raised when forbidden market data endpoints are accessed."""


class ZerodhaClient:
    """
    Client wrapper encapsulating official KiteConnect SDK instance.
    """

    def __init__(
        self,
        api_key: str | None = None,
        access_token: str | None = None,
        kite_instance: KiteConnect | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("ZERODHA_API_KEY", "")
        self.access_token = access_token or os.getenv("ZERODHA_ACCESS_TOKEN", "")

        if kite_instance:
            self.kite = kite_instance
        else:
            self.kite = KiteConnect(api_key=self.api_key)
            if self.access_token:
                self.kite.set_access_token(self.access_token)

        self._last_req_time = 0.0
        self._min_interval = 0.1  # 10 requests per second rate limit

    def set_access_token(self, access_token: str) -> None:
        """Set active access token on underlying KiteConnect SDK."""
        self.access_token = access_token
        self.kite.set_access_token(access_token)

    def _rate_limit(self) -> None:
        """Enforce 10 req/sec client-side rate limit."""
        elapsed = time.time() - self._last_req_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_req_time = time.time()

    def _execute(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute KiteConnect API function call with rate limit and exception mapping."""
        self._rate_limit()
        try:
            return func(*args, **kwargs)
        except TokenException as exc:
            logger.error("Zerodha session token invalid/expired: %s", str(exc))
            raise PermissionError(f"Zerodha authentication token expired: {exc}") from exc
        except PermissionException as exc:
            logger.error("Zerodha permission denied: %s", str(exc))
            raise PermissionError(f"Zerodha permission denied: {exc}") from exc
        except OrderException as exc:
            logger.error("Zerodha order exception: %s", str(exc))
            raise ValueError(f"Zerodha order rejected: {exc}") from exc
        except (InputException, DataException) as exc:
            logger.error("Zerodha input data exception: %s", str(exc))
            raise ValueError(f"Zerodha invalid request parameters: {exc}") from exc
        except NetworkException as exc:
            logger.error("Zerodha network timeout error: %s", str(exc))
            raise OSError(f"Network error connecting to Zerodha: {exc}") from exc
        except KiteException as exc:
            logger.error("Zerodha general SDK exception: %s", str(exc))
            raise RuntimeError(f"Zerodha API error: {exc}") from exc

    def profile(self) -> dict[str, Any]:
        """Fetch user profile."""
        res = self._execute(self.kite.profile)
        return cast(dict[str, Any], res if isinstance(res, dict) else {})

    def holdings(self) -> list[dict[str, Any]]:
        """Fetch equity CNC holdings."""
        res = self._execute(self.kite.holdings)
        return cast(list[dict[str, Any]], res if isinstance(res, list) else [])

    def positions(self) -> dict[str, Any]:
        """Fetch net and day positions."""
        res = self._execute(self.kite.positions)
        return cast(dict[str, Any], res if isinstance(res, dict) else {})

    def margins(self, segment: str | None = None) -> dict[str, Any]:
        """Fetch account margins."""
        if segment:
            res = self._execute(self.kite.margins, segment=segment)
        else:
            res = self._execute(self.kite.margins)
        return cast(dict[str, Any], res if isinstance(res, dict) else {})

    def orders(self) -> list[dict[str, Any]]:
        """Fetch session order book."""
        res = self._execute(self.kite.orders)
        return cast(list[dict[str, Any]], res if isinstance(res, list) else [])

    def place_order(
        self,
        variety: str,
        exchange: str,
        tradingsymbol: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        price: float | None = None,
        trigger_price: float | None = None,
        validity: str = "DAY",
        tag: str = "moneyyyyyy",
        **kwargs: Any,
    ) -> str:
        """Place order via KiteConnect SDK."""
        params: dict[str, Any] = {
            "variety": variety,
            "exchange": exchange,
            "tradingsymbol": tradingsymbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "product": product,
            "order_type": order_type,
            "validity": validity,
            "tag": tag,
        }
        if price is not None:
            params["price"] = price
        if trigger_price is not None:
            params["trigger_price"] = trigger_price
        params.update(kwargs)

        res = self._execute(self.kite.place_order, **params)
        return str(res)

    def modify_order(
        self,
        variety: str,
        order_id: str,
        quantity: int | None = None,
        price: float | None = None,
        trigger_price: float | None = None,
        order_type: str | None = None,
        validity: str | None = None,
    ) -> str:
        """Modify existing order via KiteConnect SDK."""
        params: dict[str, Any] = {"variety": variety, "order_id": order_id}
        if quantity is not None:
            params["quantity"] = quantity
        if price is not None:
            params["price"] = price
        if trigger_price is not None:
            params["trigger_price"] = trigger_price
        if order_type is not None:
            params["order_type"] = order_type
        if validity is not None:
            params["validity"] = validity

        res = self._execute(self.kite.modify_order, **params)
        return str(res)

    def cancel_order(self, variety: str, order_id: str) -> str:
        """Cancel order via KiteConnect SDK."""
        res = self._execute(self.kite.cancel_order, variety=variety, order_id=order_id)
        return str(res)

    def get_gtts(self) -> list[dict[str, Any]]:
        """Fetch list of GTT triggers."""
        res = self._execute(self.kite.get_gtts)
        return cast(list[dict[str, Any]], res if isinstance(res, list) else [])

    def place_gtt(
        self,
        trigger_type: str,
        tradingsymbol: str,
        exchange: str,
        trigger_values: list[float],
        last_price: float,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Place a GTT trigger rule."""
        res = self._execute(
            self.kite.place_gtt,
            trigger_type=trigger_type,
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            trigger_values=trigger_values,
            last_price=last_price,
            orders=orders,
        )
        return cast(dict[str, Any], res if isinstance(res, dict) else {})

    def quote(self, instruments: list[str]) -> dict[str, Any]:
        """Fetch live quotes for instruments (e.g. ['NSE:RELIANCE', 'NSE:INFY'])."""
        res = self._execute(self.kite.quote, instruments)
        return cast(dict[str, Any], res if isinstance(res, dict) else {})

    def historical_data(
        self, instrument_token: int, from_date: str, to_date: str, interval: str
    ) -> list[dict[str, Any]]:
        """Fetch historical candles for an instrument token."""
        res = self._execute(
            self.kite.historical_data,
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
        )
        return cast(list[dict[str, Any]], res if isinstance(res, list) else [])
