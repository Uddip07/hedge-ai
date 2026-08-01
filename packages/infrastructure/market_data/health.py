"""
Market Data Health Diagnostics.

Aggregates diagnostic and health status across provider categories.
"""

from typing import Any

from packages.infrastructure.market_data.registries.base_registry import BaseProviderRegistry


class MarketDataHealthCheck:
    """
    Health check diagnostic runner for Market Data Infrastructure.
    """

    def __init__(self, registries: list[BaseProviderRegistry[Any]] | None = None) -> None:
        self.registries = registries or []

    def health_check(self) -> dict[str, Any]:
        """
        Run health check across all registered provider categories.
        """
        category_status: dict[str, Any] = {}
        for reg in self.registries:
            category_status[reg.category_name] = {
                "registered_providers": reg.list_providers(),
                "status": "HEALTHY" if reg.list_providers() else "DEGRADED",
            }

        return {
            "status": "HEALTHY",
            "categories": category_status,
        }
