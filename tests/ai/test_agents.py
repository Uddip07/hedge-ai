"""
Unit tests for AI specialized research agents.
"""

import unittest

from packages.ai.agents import (
    FundamentalAgent,
    MacroAgent,
    NewsAgent,
    RiskAgent,
    TechnicalAgent,
)
from packages.ai.models import AgentContext, AgentResult
from packages.domain.enums.ai import AgentType
from packages.domain.value_objects.identifiers import Ticker


class TestAIAgents(unittest.TestCase):
    def setUp(self) -> None:
        self.context = AgentContext(ticker=Ticker("RELIANCE.NSE"))

    def test_fundamental_agent(self) -> None:
        agent = FundamentalAgent()
        self.assertEqual(agent.agent_type, AgentType.FUNDAMENTAL)
        self.assertTrue(agent.system_prompt_location.endswith("fundamental_agent_v1.txt"))
        self.assertIsNotNone(agent.output_schema)
        self.assertIsNotNone(agent.metadata)

        result = agent.analyze(self.context)
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.agent_type, AgentType.FUNDAMENTAL)
        self.assertEqual(result.recommendation.value, "BUY")
        self.assertGreaterEqual(result.execution_time_ms, 0.0)

    def test_technical_agent(self) -> None:
        agent = TechnicalAgent()
        self.assertEqual(agent.agent_type, AgentType.QUANT)
        result = agent.analyze(self.context)
        self.assertEqual(result.agent_type, AgentType.QUANT)

    def test_news_agent(self) -> None:
        agent = NewsAgent()
        self.assertEqual(agent.agent_type, AgentType.SENTIMENT)
        result = agent.analyze(self.context)
        self.assertEqual(result.agent_type, AgentType.SENTIMENT)

    def test_risk_agent(self) -> None:
        agent = RiskAgent()
        self.assertEqual(agent.agent_type, AgentType.RISK)
        result = agent.analyze(self.context)
        self.assertEqual(result.agent_type, AgentType.RISK)

    def test_macro_agent(self) -> None:
        agent = MacroAgent()
        self.assertEqual(agent.agent_type, AgentType.MACRO)
        result = agent.analyze(self.context)
        self.assertEqual(result.agent_type, AgentType.MACRO)


if __name__ == "__main__":
    unittest.main()
