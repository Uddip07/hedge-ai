"""
LLM Provider Registry for Multi-Provider AI Framework.

Maintains registered LLMPort adapter instances and capability metadata per provider.
"""

from packages.application.ports.llm_port import LLMPort
from packages.infrastructure.llm.capabilities import ProviderCapabilities
from packages.infrastructure.llm.providers.claude import ClaudeAdapter
from packages.infrastructure.llm.providers.deepseek import DeepSeekAdapter
from packages.infrastructure.llm.providers.gemini import GeminiAdapter
from packages.infrastructure.llm.providers.local import LocalLLMAdapter
from packages.infrastructure.llm.providers.openai import OpenAIAdapter


class LLMProviderRegistry:
    """
    Registry maintaining LLMPort adapters and capability descriptors.
    """

    def __init__(self) -> None:
        self._providers: dict[str, LLMPort] = {}
        self._capabilities: dict[str, ProviderCapabilities] = {}
        self._register_defaults()

    def register_provider(
        self,
        name: str,
        adapter: LLMPort,
        capabilities: ProviderCapabilities | None = None,
    ) -> None:
        """Register or override an LLMPort provider and capabilities."""
        p_name = name.lower()
        self._providers[p_name] = adapter
        self._capabilities[p_name] = capabilities or ProviderCapabilities(provider_name=p_name)

    def get_provider(self, name: str) -> LLMPort:
        """Fetch LLMPort adapter by provider name."""
        p_name = name.lower()
        if p_name not in self._providers:
            raise KeyError(f"LLM Provider '{name}' is not registered.")
        return self._providers[p_name]

    def get_capabilities(self, name: str) -> ProviderCapabilities:
        """Fetch ProviderCapabilities by provider name."""
        p_name = name.lower()
        if p_name not in self._capabilities:
            return ProviderCapabilities(provider_name=p_name)
        return self._capabilities[p_name]

    def list_providers(self) -> list[str]:
        """List registered provider names."""
        return list(self._providers.keys())

    def _register_defaults(self) -> None:
        """Initialize standard provider adapters."""
        self.register_provider(
            "gemini",
            GeminiAdapter(),
            ProviderCapabilities(
                provider_name="gemini",
                supports_structured_output=True,
                max_context_window=1000000,
                cost_per_1k_input_tokens=0.000125,
                cost_per_1k_output_tokens=0.000375,
            ),
        )
        self.register_provider(
            "claude",
            ClaudeAdapter(),
            ProviderCapabilities(
                provider_name="claude",
                supports_structured_output=True,
                max_context_window=200000,
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.015,
            ),
        )
        self.register_provider(
            "openai",
            OpenAIAdapter(),
            ProviderCapabilities(
                provider_name="openai",
                supports_structured_output=True,
                max_context_window=128000,
                cost_per_1k_input_tokens=0.0025,
                cost_per_1k_output_tokens=0.010,
            ),
        )
        self.register_provider(
            "deepseek",
            DeepSeekAdapter(),
            ProviderCapabilities(
                provider_name="deepseek",
                supports_structured_output=True,
                max_context_window=64000,
                cost_per_1k_input_tokens=0.0005,
                cost_per_1k_output_tokens=0.002,
            ),
        )
        self.register_provider(
            "local",
            LocalLLMAdapter(),
            ProviderCapabilities(
                provider_name="local",
                supports_structured_output=True,
                max_context_window=32000,
                cost_per_1k_input_tokens=0.0,
                cost_per_1k_output_tokens=0.0,
            ),
        )
