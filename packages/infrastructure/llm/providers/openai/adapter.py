"""
OpenAI LLM Provider Adapter Skeleton.

Implements BaseLLMAdapter and LLMPort interfaces for OpenAI GPT models.
"""

from typing import Any

from packages.domain.ai.prompt import Prompt
from packages.domain.ai.reasoning import ModelResponse
from packages.domain.enums.ai import ModelProvider
from packages.infrastructure.llm.base import BaseLLMAdapter
from packages.infrastructure.llm.config import LLMConfig
from packages.infrastructure.llm.exceptions import LLMProviderError


class OpenAIAdapter(BaseLLMAdapter):
    """
    OpenAI Adapter skeleton implementing BaseLLMAdapter and LLMPort.
    """

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig(model_name="gpt-4o")
        self.provider_name = "openai"

    def model_info(self) -> dict[str, Any]:
        return {
            "provider": ModelProvider.OPENAI.value,
            "model_name": self.config.model_name,
        }

    def token_count(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    def health_check(self) -> bool:
        return True

    def generate(
        self,
        prompt_text: str,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> str:
        if not self.config.api_key:
            raise LLMProviderError(
                "OpenAI API key is not configured.",
                context={"provider": self.provider_name},
            )
        return f"[OpenAI Mock Response] Analysis for: {prompt_text[:30]}..."

    def structured_generate(
        self,
        prompt_text: str,
        response_schema: dict[str, Any],
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not self.config.api_key:
            raise LLMProviderError(
                "OpenAI API key is not configured.",
                context={"provider": self.provider_name},
            )
        return {
            "recommendation": "BUY",
            "score": 0.82,
            "confidence": 0.88,
            "reasoning": "[OpenAI Structured Response] Strong earnings growth.",
        }

    def generate_response(self, prompt: Prompt) -> ModelResponse:
        latest_ver = prompt.versions[-1] if prompt.versions else None
        p_text = latest_ver.template if latest_ver else prompt.name
        content = self.generate(p_text)
        return ModelResponse(
            provider=ModelProvider.OPENAI,
            model_name=self.config.model_name,
            content=content,
            prompt_tokens=self.token_count(p_text),
            completion_tokens=self.token_count(content),
            latency_ms=100.0,
        )

    def generate_structured_output(
        self, prompt_text: str, response_schema: dict[str, Any]
    ) -> dict[str, Any]:
        return self.structured_generate(prompt_text, response_schema)
