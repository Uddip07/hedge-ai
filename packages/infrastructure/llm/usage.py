"""
Usage Tracker for Multi-Provider AI Framework.

Tracks token counts, execution latencies, request volumes, and estimated financial costs per provider.
"""

from typing import Any

from packages.infrastructure.llm.capabilities import ProviderCapabilities


class UsageTracker:
    """
    Tracker calculating per-provider usage telemetry and financial cost estimates.
    """

    def __init__(self) -> None:
        self._input_tokens: dict[str, int] = {}
        self._output_tokens: dict[str, int] = {}
        self._request_counts: dict[str, int] = {}
        self._total_costs_usd: dict[str, float] = {}

    def track_usage(
        self,
        provider_name: str,
        input_tokens: int,
        output_tokens: int,
        capabilities: ProviderCapabilities | None = None,
    ) -> float:
        """
        Record token usage for a provider call and return estimated call cost in USD.

        Args:
            provider_name (str): Identifier name.
            input_tokens (int): Count of input tokens consumed.
            output_tokens (int): Count of output tokens generated.
            capabilities (ProviderCapabilities | None): Optional pricing capabilities descriptor.

        Returns:
            float: Estimated cost of this invocation in USD.
        """
        self._input_tokens[provider_name] = self._input_tokens.get(provider_name, 0) + input_tokens
        self._output_tokens[provider_name] = (
            self._output_tokens.get(provider_name, 0) + output_tokens
        )
        self._request_counts[provider_name] = self._request_counts.get(provider_name, 0) + 1

        in_cost_rate = capabilities.cost_per_1k_input_tokens if capabilities else 0.0005
        out_cost_rate = capabilities.cost_per_1k_output_tokens if capabilities else 0.0015

        call_cost = ((input_tokens / 1000.0) * in_cost_rate) + (
            (output_tokens / 1000.0) * out_cost_rate
        )

        self._total_costs_usd[provider_name] = (
            self._total_costs_usd.get(provider_name, 0.0) + call_cost
        )
        return call_cost

    def get_provider_usage(self, provider_name: str) -> dict[str, Any]:
        """Fetch usage telemetry dictionary for a specific provider."""
        return {
            "provider_name": provider_name,
            "requests": self._request_counts.get(provider_name, 0),
            "input_tokens": self._input_tokens.get(provider_name, 0),
            "output_tokens": self._output_tokens.get(provider_name, 0),
            "total_tokens": self._input_tokens.get(provider_name, 0)
            + self._output_tokens.get(provider_name, 0),
            "total_cost_usd": round(self._total_costs_usd.get(provider_name, 0.0), 6),
        }

    def get_total_usage_report(self) -> dict[str, Any]:
        """Fetch comprehensive usage telemetry report across all providers."""
        all_providers = set(self._request_counts.keys())
        providers_report = {p: self.get_provider_usage(p) for p in all_providers}

        grand_input = sum(self._input_tokens.values())
        grand_output = sum(self._output_tokens.values())
        grand_requests = sum(self._request_counts.values())
        grand_cost = sum(self._total_costs_usd.values())

        return {
            "total_requests": grand_requests,
            "total_input_tokens": grand_input,
            "total_output_tokens": grand_output,
            "total_tokens": grand_input + grand_output,
            "total_cost_usd": round(grand_cost, 6),
            "providers": providers_report,
        }
