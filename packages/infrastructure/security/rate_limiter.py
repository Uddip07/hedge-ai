"""
Authentication Endpoint In-Memory Rate Limiter.
"""

from datetime import UTC, datetime

from packages.domain.exceptions.base import DomainError


class RateLimitExceededError(DomainError):
    """Raised when authentication endpoint request rate limit is exceeded."""

    DEFAULT_CODE = "RATE_LIMIT_EXCEEDED"


class SimpleRateLimiter:
    """
    In-memory fixed window rate limiter for auth endpoints.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}

    def check_rate_limit(self, key: str) -> None:
        now = datetime.now(UTC).timestamp()
        cutoff = now - self.window_seconds
        history = self.requests.get(key, [])
        history = [ts for ts in history if ts > cutoff]

        if len(history) >= self.max_requests:
            raise RateLimitExceededError(
                f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds allowed.",
                context={"limit": self.max_requests, "window_seconds": self.window_seconds},
            )

        history.append(now)
        self.requests[key] = history


auth_rate_limiter = SimpleRateLimiter(max_requests=10, window_seconds=60)
