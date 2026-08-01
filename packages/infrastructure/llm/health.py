"""
Provider Health Monitor for Multi-Provider AI Framework.

Tracks provider availability, error counts, latency, and health status states (HEALTHY, DEGRADED, UNHEALTHY).
"""

from datetime import UTC, datetime
from typing import Any


class ProviderHealthMonitor:
    """
    Health monitor evaluating provider uptime and failure rates.
    """

    STATUS_HEALTHY = "HEALTHY"
    STATUS_DEGRADED = "DEGRADED"
    STATUS_UNHEALTHY = "UNHEALTHY"

    def __init__(self, failure_threshold: int = 3) -> None:
        self.failure_threshold = failure_threshold
        self._status_map: dict[str, str] = {}
        self._consecutive_failures: dict[str, int] = {}
        self._last_check_time: dict[str, str] = {}

    def get_status(self, provider_name: str) -> str:
        """Get current health status of a provider."""
        return self._status_map.get(provider_name, self.STATUS_HEALTHY)

    def is_healthy(self, provider_name: str) -> bool:
        """Return True if provider is HEALTHY or DEGRADED (available for traffic)."""
        return self.get_status(provider_name) != self.STATUS_UNHEALTHY

    def record_success(self, provider_name: str) -> None:
        """Record successful invocation for a provider."""
        self._consecutive_failures[provider_name] = 0
        self._status_map[provider_name] = self.STATUS_HEALTHY
        self._last_check_time[provider_name] = datetime.now(UTC).isoformat()

    def record_failure(self, provider_name: str) -> None:
        """Record failure invocation for a provider."""
        current_fails = self._consecutive_failures.get(provider_name, 0) + 1
        self._consecutive_failures[provider_name] = current_fails
        self._last_check_time[provider_name] = datetime.now(UTC).isoformat()

        if current_fails >= self.failure_threshold:
            self._status_map[provider_name] = self.STATUS_UNHEALTHY
        else:
            self._status_map[provider_name] = self.STATUS_DEGRADED

    def get_health_report(self) -> dict[str, Any]:
        """Return complete health status report dictionary across all tracked providers."""
        report = {}
        all_providers = set(self._status_map.keys()).union(self._consecutive_failures.keys())
        for p in all_providers:
            report[p] = {
                "status": self.get_status(p),
                "consecutive_failures": self._consecutive_failures.get(p, 0),
                "last_check": self._last_check_time.get(p, "Never"),
            }
        return report
