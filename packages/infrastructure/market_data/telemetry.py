"""
Market Data Telemetry Collector.

Captures request diagnostics, latency metrics, cache hit status, and provider
error traces within the Infrastructure Layer.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, slots=True)
class TelemetryRecord:
    """
    Individual market data request telemetry log record.
    """

    request_id: str
    provider: str
    operation: str
    ticker: str
    latency_ms: float
    cache_hit: bool
    success: bool
    failure_reason: str | None = None
    timestamp: str = field(default_factory=lambda: Timestamp.now_utc().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize record to dictionary."""
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "operation": self.operation,
            "ticker": self.ticker,
            "latency_ms": self.latency_ms,
            "cache_hit": self.cache_hit,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "timestamp": self.timestamp,
        }


class MarketDataTelemetry:
    """
    In-memory telemetry collector for Market Data infrastructure diagnostics.
    """

    def __init__(self) -> None:
        self._records: list[TelemetryRecord] = []

    def record_event(
        self,
        provider: str,
        operation: str,
        ticker: str,
        latency_ms: float,
        cache_hit: bool,
        success: bool,
        failure_reason: str | None = None,
        request_id: str | None = None,
    ) -> TelemetryRecord:
        """
        Record a market data request event.
        """
        rec = TelemetryRecord(
            request_id=request_id or str(uuid.uuid4()),
            provider=provider,
            operation=operation,
            ticker=ticker,
            latency_ms=latency_ms,
            cache_hit=cache_hit,
            success=success,
            failure_reason=failure_reason,
        )
        self._records.append(rec)
        return rec

    def get_records(self) -> list[TelemetryRecord]:
        """Retrieve all recorded telemetry events."""
        return list(self._records)

    def clear(self) -> None:
        """Clear recorded telemetry events."""
        self._records.clear()


class TelemetryTimer:
    """
    Context manager helper for timing market data request operations.
    """

    def __init__(self) -> None:
        self.start_time: float = 0.0
        self.latency_ms: float = 0.0

    def __enter__(self) -> "TelemetryTimer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.latency_ms = round((time.perf_counter() - self.start_time) * 1000.0, 2)
