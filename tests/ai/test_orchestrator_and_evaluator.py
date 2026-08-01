"""
Unit tests for AgentOrchestrator and AgentEvaluator.
"""

import unittest

from packages.ai import (
    AgentContext,
    AgentEvaluator,
    AgentOrchestrator,
    FundamentalAgent,
    MacroAgent,
    NewsAgent,
    RiskAgent,
    TechnicalAgent,
)
from packages.domain.value_objects.identifiers import Ticker


class TestOrchestratorAndEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = AgentOrchestrator(
            agents=[
                FundamentalAgent(),
                TechnicalAgent(),
                NewsAgent(),
                RiskAgent(),
                MacroAgent(),
            ]
        )
        self.evaluator = AgentEvaluator()

    def test_run_analysis_orchestration(self) -> None:
        context = AgentContext(ticker=Ticker("TCS.NSE"))
        consensus, results = self.orchestrator.run_analysis(context)

        self.assertEqual(len(results), 5)
        self.assertIsNotNone(consensus)
        self.assertGreater(float(consensus.consensus_score.value), 0.0)

        # Verify session memory persistence
        stored_results = self.orchestrator.memory_store.get_agent_results(context.session_id)
        self.assertEqual(len(stored_results), 5)

        stored_consensus = self.orchestrator.memory_store.get_consensus(context.session_id)
        self.assertIsNotNone(stored_consensus)

    def test_evaluator_metrics(self) -> None:
        context = AgentContext(ticker=Ticker("INFY.NSE"))
        consensus, results = self.orchestrator.run_analysis(context)

        eval_res = self.evaluator.evaluate_result(results[0])
        self.assertTrue(eval_res["is_compliant"])

        eval_con = self.evaluator.evaluate_consensus(consensus)
        self.assertTrue(eval_con["is_valid"])


if __name__ == "__main__":
    unittest.main()
