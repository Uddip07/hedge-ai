"""
Fallback Strategy for Multi-Provider AI Framework.

Executes requests across an ordered fallback chain when primary providers fail or report unhealthy status.
"""

from collections.abc import Callable
from typing import Any

from packages.infrastructure.llm.exceptions import LLMProviderError
from packages.infrastructure.llm.health import ProviderHealthMonitor


class FallbackStrategy:
    """
    Strategy managing ordered fallback executions across registered LLM providers.
    """

    DEFAULT_FALLBACK_CHAIN = ["gemini", "claude", "openai", "deepseek", "local"]

    def __init__(
        self,
        fallback_chain: list[str] | None = None,
        health_monitor: ProviderHealthMonitor | None = None,
    ) -> None:
        self.fallback_chain = fallback_chain or list(self.DEFAULT_FALLBACK_CHAIN)
        self.health_monitor = health_monitor or ProviderHealthMonitor()

    def execute_with_fallback(
        self,
        execute_func: Callable[[str], Any],
        primary_provider: str = "gemini",
    ) -> tuple[Any, str]:
        """
        Execute function trying primary_provider first, falling back to ordered alternatives upon error.

        Args:
            execute_func (Callable[[str], Any]): Function taking provider_name and returning response.
            primary_provider (str): Target primary provider identifier.

        Returns:
            tuple[Any, str]: (result_payload, winning_provider_name)
        """
        chain = [primary_provider] + [p for p in self.fallback_chain if p != primary_provider]

        last_error: Exception | None = None

        for provider in chain:
            if not self.health_monitor.is_healthy(provider):
                continue

            try:
                res = execute_func(provider)
                self.health_monitor.record_success(provider)
                return res, provider
            except Exception as exc:
                self.health_monitor.record_failure(provider)
                last_error = exc

        if last_error:
            raise LLMProviderError(
                f"All LLM providers in fallback chain failed. Last error: {last_error}",
                context={"provider": "all"},
            ) from last_error

        raise LLMProviderError(
            "No healthy LLM provider available in fallback chain.",
            context={"provider": "all"},
        )
