"""
Request Logging Middleware for MONEYYYYYY API.

Logs incoming request metadata and execution status using StructuredLogger.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from packages.infrastructure.logging import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware logging HTTP requests and response status codes.
    """

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.logger = get_logger(name="ihf_ai.api.middleware.logging")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        req_id = getattr(request.state, "request_id", "N/A")
        self.logger.info(
            f"HTTP {request.method} {request.url.path}",
            context={
                "request_id": req_id,
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else "unknown",
            },
        )
        response = await call_next(request)
        self.logger.info(
            f"HTTP {request.method} {request.url.path} -> {response.status_code}",
            context={
                "request_id": req_id,
                "status_code": response.status_code,
            },
        )
        return response
