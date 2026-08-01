"""
Unit tests for Prompt Intelligence Framework.
"""

import unittest
from decimal import Decimal
from unittest.mock import MagicMock

from packages.ai.agents.fundamental_agent import FundamentalAgent
from packages.ai.models import AgentContext
from packages.ai.prompts import (
    ContextBuilder,
    PromptComposer,
    PromptValidator,
    PromptVersionManager,
    TokenBudgetManager,
)
from packages.ai.prompts.prompt_registry import PromptRegistry
from packages.application.ports.llm_port import LLMPort
from packages.domain.ai.reasoning import Evidence
from packages.domain.enums.ai import AgentType
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.metrics.scores import ConfidenceScore
from packages.infrastructure.llm.exceptions import LLMValidationError


class TestPromptIntelligenceFramework(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = PromptRegistry()
        self.validator = PromptValidator()
        self.version_manager = PromptVersionManager()
        self.token_budget = TokenBudgetManager()
        self.context_builder = ContextBuilder()
        self.composer = PromptComposer(
            context_builder=self.context_builder,
            token_budget_manager=self.token_budget,
            validator=self.validator,
        )

        self.ticker = Ticker("RELIANCE")
        self.context = AgentContext(ticker=self.ticker)

    def test_prompt_registry_disk_loading_and_caching(self) -> None:
        template = self.registry.get_template(AgentType.FUNDAMENTAL)
        self.assertIsNotNone(template)
        self.assertIn("RELIANCE", template.render_system_prompt(ticker="RELIANCE"))
        self.assertIn("recommendation", template.output_schema.get("properties", {}))

    def test_prompt_validator_placeholders_and_sections(self) -> None:
        prompt_text = "System prompt for {ticker}. Market: {market_data}. Evidence: {rag_evidence}."
        self.assertTrue(
            self.validator.validate_placeholders(prompt_text, ["ticker", "market_data"])
        )
        self.assertFalse(
            self.validator.validate_placeholders(prompt_text, ["ticker", "missing_var"])
        )

        self.assertTrue(
            self.validator.validate_required_sections(prompt_text, ["System prompt", "Market:"])
        )

    def test_prompt_validator_response_json(self) -> None:
        schema = {"type": "object", "required": ["recommendation", "score"]}
        valid_response = {"recommendation": "BUY", "score": 0.80}
        invalid_response = {"score": 0.80}

        self.assertTrue(self.validator.validate_response_json(valid_response, schema))
        with self.assertRaises(LLMValidationError):
            self.validator.validate_response_json(invalid_response, schema)

    def test_token_budget_manager_trimming(self) -> None:
        ev1 = Evidence(fact="High ROCE 22%", confidence=ConfidenceScore(Decimal("0.95")))
        ev2 = Evidence(
            fact="Low confidence rumor item", confidence=ConfidenceScore(Decimal("0.30"))
        )

        # Small budget (4 tokens) only permits high-confidence ev1 (3 tokens)
        trimmed = self.token_budget.trim_evidence_context([ev1, ev2], max_tokens=4)
        self.assertEqual(len(trimmed), 1)
        self.assertEqual(trimmed[0].fact, "High ROCE 22%")

    def test_context_builder(self) -> None:
        m_str = self.context_builder.format_market_data({"price": 2450.50, "status": "ACTIVE"})
        self.assertIn("price: 2450.5", m_str)

        vars_map = self.context_builder.build_full_context(
            self.context, market_data={"price": 2500}
        )
        self.assertEqual(vars_map["ticker"], "RELIANCE")

    def test_prompt_composer(self) -> None:
        system_tmpl = "Analyze {ticker}.\n\nMarket:\n{market_data}\n\nEvidence:\n{rag_evidence}"
        sys_prompt, user_prompt = self.composer.compose_prompt(
            system_prompt_template=system_tmpl,
            agent_context=self.context,
            market_data={"status": "ACTIVE"},
            rag_evidence=[
                Evidence(fact="Strong earnings", confidence=ConfidenceScore(Decimal("0.90")))
            ],
        )

        self.assertIn("RELIANCE", sys_prompt)
        self.assertIn("Strong earnings", sys_prompt)
        self.assertIsNotNone(user_prompt)

    def test_fundamental_agent_integration(self) -> None:
        agent = FundamentalAgent(
            prompt_registry=self.registry,
            composer=self.composer,
            validator=self.validator,
        )

        res = agent.analyze(self.context)
        self.assertEqual(res.agent_type, AgentType.FUNDAMENTAL)
        self.assertGreater(len(res.evidence), 0)

        # Test with mock LLMPort
        mock_llm = MagicMock(spec=LLMPort)
        mock_llm.generate_structured_output.return_value = {
            "recommendation": "BUY",
            "score": 0.85,
            "confidence": 0.90,
            "reasoning": "LLM fundamental balance sheet strength confirmed.",
        }

        agent_llm = FundamentalAgent(
            prompt_registry=self.registry,
            llm_port=mock_llm,
            composer=self.composer,
            validator=self.validator,
        )

        res_llm = agent_llm.analyze(self.context)
        self.assertEqual(res_llm.recommendation.value, "BUY")
        self.assertEqual(res_llm.reasoning, "LLM fundamental balance sheet strength confirmed.")


if __name__ == "__main__":
    unittest.main()
