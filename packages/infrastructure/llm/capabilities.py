"""
Provider Capabilities Model for Multi-Provider AI Framework.

Defines feature capabilities, token limits, and pricing metadata per LLM provider.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderCapabilities:
    """
    Metadata capabilities descriptor for an LLM provider.

    Attributes:
        provider_name (str): Identifier name (gemini, claude, openai, deepseek, local).
        supports_structured_output (bool): True if native JSON schema enforcement is supported.
        supports_streaming (bool): True if token streaming is supported.
        max_context_window (int): Maximum input token window size.
        cost_per_1k_input_tokens (float): Cost in USD per 1,000 input tokens.
        cost_per_1k_output_tokens (float): Cost in USD per 1,000 output tokens.
        metadata (dict[str, Any]): Additional model capabilities metadata.
    """

    provider_name: str
    supports_structured_output: bool = True
    supports_streaming: bool = True
    max_context_window: int = 128000
    cost_per_1k_input_tokens: float = 0.0005
    cost_per_1k_output_tokens: float = 0.0015
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize ProviderCapabilities to dictionary."""
        return {
            "provider_name": self.provider_name,
            "supports_structured_output": self.supports_structured_output,
            "supports_streaming": self.supports_streaming,
            "max_context_window": self.max_context_window,
            "cost_per_1k_input_tokens": self.cost_per_1k_input_tokens,
            "cost_per_1k_output_tokens": self.cost_per_1k_output_tokens,
            "metadata": self.metadata,
        }
