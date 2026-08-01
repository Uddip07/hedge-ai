"""
Mock LLM Adapter for Infrastructure Layer.

Provides deterministic model reasoning responses for offline development and unit tests.
Zero external LLM API calls (OpenAI, Gemini, Anthropic).
"""

from typing import Any

from packages.application.ports.llm_port import LLMPort
from packages.domain.ai.prompt import Prompt
from packages.domain.ai.reasoning import ModelResponse
from packages.domain.enums.ai import ModelProvider


class MockLLMAdapter(LLMPort):
    """
    Mock Adapter implementing LLMPort.
    """

    def generate_response(self, prompt: Prompt) -> ModelResponse:
        return ModelResponse(
            provider=ModelProvider.OPENAI,
            model_name="mock-gpt-4o",
            content=f"Deterministic mock AI response generated for prompt '{prompt.name}'.",
            prompt_tokens=50,
            completion_tokens=100,
            latency_ms=120.0,
        )

    def generate_structured_output(
        self,
        prompt_text: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "status": "SUCCESS",
            "summary": f"Mock structured response for prompt: {prompt_text[:30]}...",
            "confidence": 0.85,
        }
