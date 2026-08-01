"""
Unit tests for Multi-Provider AI Framework.
"""

import unittest

from packages.infrastructure.llm import (
    ClaudeAdapter,
    DeepSeekAdapter,
    FallbackStrategy,
    LLMConfig,
    LLMProviderError,
    LLMProviderRegistry,
    LLMRouter,
    LocalLLMAdapter,
    OpenAIAdapter,
    ProviderCapabilities,
    ProviderHealthMonitor,
    UsageTracker,
)


class TestMultiProviderAIFramework(unittest.TestCase):
    def setUp(self) -> None:
        self.health_monitor = ProviderHealthMonitor(failure_threshold=2)
        self.usage_tracker = UsageTracker()
        self.registry = LLMProviderRegistry()
        self.fallback_strategy = FallbackStrategy(health_monitor=self.health_monitor)

        self.router = LLMRouter(
            registry=self.registry,
            health_monitor=self.health_monitor,
            usage_tracker=self.usage_tracker,
            fallback_strategy=self.fallback_strategy,
            default_provider="local",
        )

    def test_provider_capabilities(self) -> None:
        caps = ProviderCapabilities(
            provider_name="test-prov",
            max_context_window=64000,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002,
        )
        self.assertEqual(caps.provider_name, "test-prov")
        self.assertEqual(caps.max_context_window, 64000)

    def test_provider_health_monitor_transitions(self) -> None:
        p_name = "test-health-provider"
        self.assertTrue(self.health_monitor.is_healthy(p_name))

        self.health_monitor.record_failure(p_name)
        self.assertEqual(self.health_monitor.get_status(p_name), "DEGRADED")

        self.health_monitor.record_failure(p_name)
        self.assertEqual(self.health_monitor.get_status(p_name), "UNHEALTHY")
        self.assertFalse(self.health_monitor.is_healthy(p_name))

        self.health_monitor.record_success(p_name)
        self.assertTrue(self.health_monitor.is_healthy(p_name))

    def test_usage_tracker_cost_calculation(self) -> None:
        cost = self.usage_tracker.track_usage("gemini", input_tokens=1000, output_tokens=1000)
        self.assertGreater(cost, 0.0)

        report = self.usage_tracker.get_total_usage_report()
        self.assertEqual(report["total_requests"], 1)
        self.assertEqual(report["total_tokens"], 2000)

    def test_llm_provider_registry(self) -> None:
        providers = self.registry.list_providers()
        self.assertIn("gemini", providers)
        self.assertIn("claude", providers)
        self.assertIn("openai", providers)
        self.assertIn("deepseek", providers)
        self.assertIn("local", providers)

        local_adapter = self.registry.get_provider("local")
        self.assertIsNotNone(local_adapter)

    def test_fallback_strategy_execution(self) -> None:
        calls: list[str] = []

        def mock_exec(p: str) -> str:
            calls.append(p)
            if p == "primary-failing":
                raise LLMProviderError("Primary provider failed", context={"provider": p})
            return "Fallback Success Response"

        strategy = FallbackStrategy(
            fallback_chain=["primary-failing", "secondary-working"],
            health_monitor=self.health_monitor,
        )

        res, winning = strategy.execute_with_fallback(
            execute_func=mock_exec,
            primary_provider="primary-failing",
        )

        self.assertEqual(winning, "secondary-working")
        self.assertEqual(res, "Fallback Success Response")
        self.assertIn("primary-failing", calls)
        self.assertIn("secondary-working", calls)

    def test_llm_router_text_generation(self) -> None:
        res = self.router.generate_text("Analyze RELIANCE fundamentals", provider_name="local")
        self.assertIn("[Local LLM Response]", res)

        # Usage tracked
        report = self.usage_tracker.get_provider_usage("local")
        self.assertEqual(report["requests"], 1)

    def test_llm_router_structured_output(self) -> None:
        schema = {"type": "object", "properties": {"recommendation": {"type": "string"}}}
        structured = self.router.generate_structured_output(
            prompt_text="Analyze TCS ROCE",
            response_schema=schema,
            provider_name="local",
        )

        self.assertIsInstance(structured, dict)
        self.assertIn("recommendation", structured)

    def test_llm_router_select_best_provider(self) -> None:
        best_min_cost = self.router.select_best_provider(strategy="min_cost")
        self.assertIsNotNone(best_min_cost)

    def test_provider_adapters_skeletons(self) -> None:
        # Mock configured API keys for skeletons
        cfg = LLMConfig(api_key="mock-api-key")

        claude = ClaudeAdapter(config=cfg)
        openai = OpenAIAdapter(config=cfg)
        deepseek = DeepSeekAdapter(config=cfg)
        local = LocalLLMAdapter()

        self.assertIn("[Claude Mock Response]", claude.generate("test prompt"))
        self.assertIn("[OpenAI Mock Response]", openai.generate("test prompt"))
        self.assertIn("[DeepSeek Mock Response]", deepseek.generate("test prompt"))
        self.assertIn("[Local LLM Response]", local.generate("test prompt"))


if __name__ == "__main__":
    unittest.main()
