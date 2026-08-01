"""
LLM Router for Multi-Provider AI Framework.

Intelligent router implementing LLMPort that routes requests across Gemini, Claude, OpenAI, DeepSeek,
and Local models based on health, capabilities, cost strategy, and fallback policies.
"""

from typing import Any, cast

from packages.application.ports.llm_port import LLMPort
from packages.domain.ai.prompt import Prompt
from packages.domain.ai.reasoning import ModelResponse
from packages.domain.enums.ai import AgentType
from packages.infrastructure.llm.fallback import FallbackStrategy
from packages.infrastructure.llm.health import ProviderHealthMonitor
from packages.infrastructure.llm.registry import LLMProviderRegistry
from packages.infrastructure.llm.usage import UsageTracker


class LLMRouter(LLMPort):
    """
    Router implementing LLMPort abstraction for multi-provider orchestration.
    """

    def __init__(
        self,
        registry: LLMProviderRegistry | None = None,
        health_monitor: ProviderHealthMonitor | None = None,
        usage_tracker: UsageTracker | None = None,
        fallback_strategy: FallbackStrategy | None = None,
        default_provider: str = "gemini",
    ) -> None:
        self.registry = registry or LLMProviderRegistry()
        self.health_monitor = health_monitor or ProviderHealthMonitor()
        self.usage_tracker = usage_tracker or UsageTracker()
        self.fallback_strategy = fallback_strategy or FallbackStrategy(
            health_monitor=self.health_monitor
        )
        self.default_provider = default_provider

    def select_best_provider(self, strategy: str = "default", min_context: int = 4096) -> str:
        """
        Select optimal provider based on strategy ('default', 'min_cost', 'performance').

        Args:
            strategy (str): Routing strategy.
            min_context (int): Required context window capacity.

        Returns:
            str: Selected provider name.
        """
        candidates = [
            p
            for p in self.registry.list_providers()
            if self.health_monitor.is_healthy(p)
            and self.registry.get_capabilities(p).max_context_window >= min_context
        ]

        if not candidates:
            return self.default_provider

        if strategy == "min_cost":
            candidates.sort(
                key=lambda p: self.registry.get_capabilities(p).cost_per_1k_input_tokens
            )
            return candidates[0]

        if self.default_provider in candidates:
            return self.default_provider

        return candidates[0]

    def generate_response(self, prompt: Prompt) -> ModelResponse:
        """
        Implementation of LLMPort interface method.
        Routes Prompt through fallback strategy to winning provider.
        """
        target = self.default_provider

        def _call_provider(p_name: str) -> ModelResponse:
            adapter = self.registry.get_provider(p_name)
            caps = self.registry.get_capabilities(p_name)
            resp = adapter.generate_response(prompt)

            # Track usage
            self.usage_tracker.track_usage(
                provider_name=p_name,
                input_tokens=resp.prompt_tokens,
                output_tokens=resp.completion_tokens,
                capabilities=caps,
            )
            return resp

        result, _ = self.fallback_strategy.execute_with_fallback(
            execute_func=_call_provider,
            primary_provider=target,
        )
        return cast(ModelResponse, result)

    def generate_text(
        self, prompt_text: str, provider_name: str | None = None, **kwargs: Any
    ) -> str:
        """
        Generate raw text response via specified or defaulted LLM provider.
        """
        target = provider_name or self.default_provider

        def _call_provider(p_name: str) -> str:
            adapter = self.registry.get_provider(p_name)
            caps = self.registry.get_capabilities(p_name)

            if hasattr(adapter, "generate"):
                res = str(adapter.generate(prompt_text, **kwargs))
            else:
                p_obj = Prompt(name="raw_prompt", agent_type=AgentType.FUNDAMENTAL)
                res = adapter.generate_response(p_obj).content

            in_toks = len(prompt_text) // 4
            out_toks = len(res) // 4
            self.usage_tracker.track_usage(
                provider_name=p_name,
                input_tokens=in_toks,
                output_tokens=out_toks,
                capabilities=caps,
            )
            return res

        result, _ = self.fallback_strategy.execute_with_fallback(
            execute_func=_call_provider,
            primary_provider=target,
        )
        return str(result)

    def generate_structured_output(
        self,
        prompt_text: str,
        response_schema: dict[str, Any],
        provider_name: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Implementation of LLMPort interface method with multi-provider routing and fallback.
        """
        target = provider_name or self.default_provider

        def _call_provider(p_name: str) -> dict[str, Any]:
            adapter = self.registry.get_provider(p_name)
            caps = self.registry.get_capabilities(p_name)
            res: dict[str, Any] = adapter.generate_structured_output(
                prompt_text=prompt_text,
                response_schema=response_schema,
            )

            # Track usage
            in_toks = len(prompt_text) // 4
            out_toks = len(str(res)) // 4
            self.usage_tracker.track_usage(
                provider_name=p_name,
                input_tokens=in_toks,
                output_tokens=out_toks,
                capabilities=caps,
            )
            return res

        result, _ = self.fallback_strategy.execute_with_fallback(
            execute_func=_call_provider,
            primary_provider=target,
        )
        return dict(result)

    def count_tokens(self, text: str, provider_name: str | None = None) -> int:
        """Count tokens using target provider adapter."""
        target = provider_name or self.default_provider
        adapter = self.registry.get_provider(target)
        if hasattr(adapter, "token_count"):
            return int(adapter.token_count(text))
        return len(text) // 4

    def health_check(self, provider_name: str | None = None) -> bool:
        """Check health status of specified or default provider."""
        target = provider_name or self.default_provider
        adapter = self.registry.get_provider(target)
        if hasattr(adapter, "health_check"):
            is_ok = bool(adapter.health_check())
        else:
            is_ok = True

        if is_ok:
            self.health_monitor.record_success(target)
        else:
            self.health_monitor.record_failure(target)
        return is_ok
