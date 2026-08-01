"""
Unit and integration tests for Infrastructure LLM framework and GeminiAdapter.
"""

import json
import unittest
from typing import Any

from packages.domain.ai.prompt import Prompt, PromptVersion
from packages.domain.enums.ai import AgentType, ModelProvider
from packages.domain.value_objects.identifiers import PromptId
from packages.infrastructure.llm import (
    GeminiAdapter,
    LLMConfig,
    LLMFactory,
    LLMMetrics,
    LLMProviderError,
    LLMValidationError,
)


class TestLLMInfrastructure(unittest.TestCase):
    def test_llm_config_defaults(self) -> None:
        cfg = LLMConfig()
        self.assertEqual(cfg.model_name, "gemini-1.5-pro")
        self.assertEqual(cfg.timeout_seconds, 30.0)
        self.assertEqual(cfg.max_retries, 3)

    def test_llm_metrics_serialization(self) -> None:
        metrics = LLMMetrics(
            model_name="gemini-1.5-pro",
            latency_ms=150.5,
            prompt_tokens=40,
            completion_tokens=60,
            total_tokens=100,
            retry_count=1,
        )
        d = metrics.to_dict()
        self.assertEqual(d["model_name"], "gemini-1.5-pro")
        self.assertEqual(d["latency_ms"], 150.5)
        self.assertEqual(d["total_tokens"], 100)

    def test_llm_factory_creation(self) -> None:
        adapter = LLMFactory.create_adapter(provider=ModelProvider.DEEPMIND)
        self.assertIsInstance(adapter, GeminiAdapter)
        info = adapter.model_info()
        self.assertEqual(info["provider"], "DEEPMIND")

    def test_gemini_adapter_text_generation(self) -> None:
        def mock_client(prompt: str, **kwargs: Any) -> str:
            return "Mock Gemini response text."

        adapter = GeminiAdapter(client=mock_client)

        res = adapter.generate("Hello Gemini")
        self.assertEqual(res, "Mock Gemini response text.")
        self.assertIsNotNone(adapter.last_metrics)
        if adapter.last_metrics:
            self.assertEqual(adapter.last_metrics.model_name, "gemini-1.5-pro")

    def test_gemini_adapter_structured_generate_success(self) -> None:
        mock_json_str = json.dumps(
            {
                "recommendation": "BUY",
                "score": 0.85,
                "confidence": 0.90,
                "reasoning": "Strong quarterly ROCE growth.",
            }
        )

        def mock_client(prompt: str, **kwargs: Any) -> str:
            return f"```json\n{mock_json_str}\n```"

        adapter = GeminiAdapter(client=mock_client)

        schema = {"type": "object"}
        result = adapter.structured_generate("Analyze RELIANCE", schema)
        self.assertEqual(result["recommendation"], "BUY")
        self.assertEqual(result["score"], 0.85)

    def test_gemini_adapter_structured_generate_invalid_json_raises(self) -> None:
        def mock_client(prompt: str, **kwargs: Any) -> str:
            return "NOT VALID JSON OBJECT"

        adapter = GeminiAdapter(client=mock_client)

        with self.assertRaises(LLMValidationError):
            adapter.structured_generate("Analyze RELIANCE", {"type": "object"})

    def test_gemini_adapter_retry_failure_raises_provider_error(self) -> None:
        def failing_client(prompt: str, **kwargs: Any) -> str:
            raise RuntimeError("API Connection Error")

        cfg = LLMConfig(max_retries=1, backoff_factor=1.1)
        adapter = GeminiAdapter(config=cfg, client=failing_client)

        with self.assertRaises(LLMProviderError):
            adapter.generate("Analyze TCS")

    def test_gemini_adapter_generate_response_llm_port(self) -> None:
        def mock_client(prompt: str, **kwargs: Any) -> str:
            return "Gemini AI response for domain prompt."

        adapter = GeminiAdapter(client=mock_client)

        version = PromptVersion(version_number="1.0.0", template="Analyze {ticker}")
        p = Prompt(
            id=PromptId.generate(),
            name="stock_analysis",
            agent_type=AgentType.FUNDAMENTAL,
            versions=[version],
        )

        model_resp = adapter.generate_response(p)
        self.assertEqual(model_resp.provider, ModelProvider.DEEPMIND)
        self.assertIn("Gemini AI response", model_resp.content)

    def test_gemini_adapter_token_count_and_health_check(self) -> None:
        def mock_client(prompt: str, **kwargs: Any) -> str:
            return "PONG"

        adapter = GeminiAdapter(client=mock_client)
        self.assertEqual(adapter.token_count("Hello World!"), 3)
        self.assertTrue(adapter.health_check())


if __name__ == "__main__":
    unittest.main()
