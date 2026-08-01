"""
LLM Adapter Factory for Infrastructure Layer.

Constructs typed LLM provider adapters based on configuration settings and ModelProvider selection.
"""

from typing import Any

from packages.domain.enums.ai import ModelProvider
from packages.infrastructure.llm.base import BaseLLMAdapter
from packages.infrastructure.llm.config import LLMConfig
from packages.infrastructure.llm.gemini_adapter import GeminiAdapter


class LLMFactory:
    """
    Factory creating BaseLLMAdapter provider instances.
    """

    @staticmethod
    def create_adapter(
        provider: ModelProvider = ModelProvider.DEEPMIND,
        config: LLMConfig | None = None,
        client: Any | None = None,
    ) -> BaseLLMAdapter:
        """
        Factory method instantiating the requested LLM provider adapter.

        Args:
            provider (ModelProvider): Targeted LLM provider enum.
            config (LLMConfig | None): Configuration settings.
            client (Any | None): Optional injected SDK client.

        Returns:
            BaseLLMAdapter: Initialized LLM provider adapter.
        """
        cfg = config or LLMConfig()

        if provider in {ModelProvider.DEEPMIND, ModelProvider.LOCAL, ModelProvider.CUSTOM}:
            return GeminiAdapter(config=cfg, client=client)

        # Default fallback to GeminiAdapter
        return GeminiAdapter(config=cfg, client=client)
