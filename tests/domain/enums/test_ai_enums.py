"""
Unit tests for AI Domain Enums.
"""

import unittest

from packages.domain.enums.ai import AgentType, ModelProvider


class TestAIEnums(unittest.TestCase):
    """Test suite for AI Enums."""

    def test_model_provider_helpers(self):
        self.assertTrue(ModelProvider.DEEPMIND.is_cloud())
        self.assertTrue(ModelProvider.LOCAL.is_local())

    def test_agent_type_helpers(self):
        self.assertTrue(AgentType.DIRECTOR.is_orchestrator())
        self.assertTrue(AgentType.QUANT.is_specialist())
        self.assertIn("director", AgentType.DIRECTOR.default_role_description().lower())


if __name__ == "__main__":
    unittest.main()
