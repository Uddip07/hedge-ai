"""
Unit tests for ConsensusEngine weighted voting logic.
"""

import unittest
from decimal import Decimal

from packages.ai.consensus import ConsensusEngine
from packages.ai.models import AgentResult
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.research.consensus import ConsensusDecision
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class TestConsensusEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ConsensusEngine()

    def test_compute_consensus_weighted(self) -> None:
        r1 = AgentResult(
            agent_type=AgentType.FUNDAMENTAL,
            recommendation=RecommendationType.BUY,
            score=RecommendationScore(Decimal("0.80")),
            confidence=ConfidenceScore(Decimal("0.90")),
            reasoning="Strong growth",
        )
        r2 = AgentResult(
            agent_type=AgentType.RISK,
            recommendation=RecommendationType.HOLD,
            score=RecommendationScore(Decimal("0.40")),
            confidence=ConfidenceScore(Decimal("0.80")),
            reasoning="Moderate risk",
        )

        weights = {
            AgentType.FUNDAMENTAL.value: Decimal("2.0"),
            AgentType.RISK.value: Decimal("1.0"),
        }

        consensus = self.engine.compute_consensus([r1, r2], agent_weights=weights)
        self.assertIsInstance(consensus, ConsensusDecision)
        self.assertEqual(len(consensus.opinions), 2)
        self.assertEqual(len(consensus.votes), 2)

        # Expected score = (0.80 * 2 + 0.40 * 1) / 3 = 2.0 / 3 = 0.6666... -> 0.67
        self.assertAlmostEqual(float(consensus.consensus_score.value), 2.0 / 3.0, places=2)

    def test_compute_consensus_empty_results(self) -> None:
        consensus = self.engine.compute_consensus([])
        self.assertEqual(len(consensus.opinions), 0)
        self.assertEqual(consensus.consensus_score.value, Decimal("0.0"))


if __name__ == "__main__":
    unittest.main()
