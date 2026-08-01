"""
Unit tests for Prompt Management System.
"""

import unittest

from packages.ai.prompts import PromptRegistry, PromptTemplate
from packages.domain.enums.ai import AgentType


class TestPromptSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = PromptRegistry()

    def test_prompt_registry_defaults(self) -> None:
        for agent_type in [
            AgentType.FUNDAMENTAL,
            AgentType.QUANT,
            AgentType.SENTIMENT,
            AgentType.RISK,
            AgentType.MACRO,
        ]:
            template = self.registry.get_template(agent_type)
            self.assertIsInstance(template, PromptTemplate)
            loc = template.system_prompt_location
            self.assertTrue(loc.endswith(".txt") or loc.endswith(".md"))
            self.assertIn("type", template.output_schema)
            self.assertIn("version", template.metadata)

    def test_prompt_rendering(self) -> None:
        template = self.registry.get_template(AgentType.FUNDAMENTAL)
        rendered = template.render_system_prompt(ticker="RELIANCE.NSE")
        self.assertIn("RELIANCE.NSE", rendered)

    def test_custom_prompt_registration(self) -> None:
        custom_template = PromptTemplate(
            agent_type=AgentType.EXECUTION,
            system_prompt_location="prompts/system/execution_v1.txt",
            system_prompt_text="Custom execution prompt for {ticker}.",
            output_schema={"type": "object"},
            metadata={"version": "2.0"},
        )
        self.registry.register(custom_template)

        fetched = self.registry.get_template(AgentType.EXECUTION)
        self.assertEqual(fetched.system_prompt_location, "prompts/system/execution_v1.txt")


if __name__ == "__main__":
    unittest.main()
