"""
Unhandled Exception Middleware for MONEYYYYYY API.

Intercepts unhandled server exceptions at the ASGI middleware boundary.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from packages.infrastructure.logging import get_logger


class UnhandledExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware catching uncaught exceptions and formatting standard 500 responses.
    """

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.logger = get_logger(name="ihf_ai.api.middleware.exception")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            req_id = getattr(request.state, "request_id", "N/A")
            self.logger.error(
                f"Unhandled Exception on {request.method} {request.url.path}: {exc}",
                context={"request_id": req_id, "error": str(exc)},
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected internal server error occurred.",
                        "details": None,
                        "request_id": req_id,
                    }
                },
            )
