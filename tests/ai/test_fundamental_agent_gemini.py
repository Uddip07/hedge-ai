"""
Integration tests for FundamentalAgent with GeminiAdapter integration.
"""

import json
import unittest
from typing import Any

from packages.ai.agents import FundamentalAgent
from packages.ai.models import AgentContext
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.identifiers import Ticker
from packages.infrastructure.llm import GeminiAdapter


class TestFundamentalAgentGemini(unittest.TestCase):
    def test_fundamental_agent_with_gemini_adapter(self) -> None:
        mock_output = json.dumps(
            {
                "recommendation": "STRONG_BUY",
                "score": 0.88,
                "confidence": 0.92,
                "reasoning": "Exceptional earnings growth, zero debt, and high moat rating for RELIANCE.NSE.",
            }
        )

        def mock_client(prompt: str, **kwargs: Any) -> str:
            return mock_output

        gemini_adapter = GeminiAdapter(client=mock_client)

        agent = FundamentalAgent(llm_port=gemini_adapter)
        context = AgentContext(ticker=Ticker("RELIANCE.NSE"))

        result = agent.analyze(context)
        self.assertEqual(result.agent_type, AgentType.FUNDAMENTAL)
        self.assertEqual(result.recommendation, RecommendationType.STRONG_BUY)
        self.assertEqual(float(result.score.value), 0.88)
        self.assertEqual(float(result.confidence.value), 0.92)
        self.assertIn("Exceptional earnings growth", result.reasoning)


if __name__ == "__main__":
    unittest.main()
