"""
Unit tests for Consensus Intelligence Engine.
"""

import unittest
from decimal import Decimal

from packages.ai.consensus import (
    AuditRecorder,
    ConfidenceEngine,
    ConflictDetector,
    ConsensusEngine,
    ConsensusIntelligenceDecision,
    DecisionExplainer,
    EvidenceAggregator,
    WeightedConsensusStrategy,
)
from packages.ai.models import AgentResult
from packages.domain.ai.reasoning import Evidence
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class TestConsensusIntelligenceEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ConsensusEngine()

        self.r_buy = AgentResult(
            agent_type=AgentType.FUNDAMENTAL,
            recommendation=RecommendationType.BUY,
            score=RecommendationScore(Decimal("0.80")),
            confidence=ConfidenceScore(Decimal("0.85")),
            reasoning="Robust ROCE and balance sheet growth",
            evidence=[Evidence(fact="ROCE 22%", confidence=ConfidenceScore(Decimal("0.90")))],
            risks=["Raw material price inflation"],
            assumptions=["Bullish earnings momentum"],
            unknowns=["Q4 export tariff updates"],
            reasoning_steps=["Analyzed P/E", "Verified ROCE"],
        )

        self.r_sell = AgentResult(
            agent_type=AgentType.RISK,
            recommendation=RecommendationType.SELL,
            score=RecommendationScore(Decimal("-0.60")),
            confidence=ConfidenceScore(Decimal("0.90")),
            reasoning="Position size limit breach and elevated VaR",
            evidence=[
                Evidence(fact="VaR threshold exceeded", confidence=ConfidenceScore(Decimal("0.95")))
            ],
            risks=["Stop loss trigger breach"],
            assumptions=["Bearish market volatility continuation"],
            unknowns=["Circuit breaker limit policy"],
            reasoning_steps=["Calculated VaR", "Evaluated position limits"],
        )

        self.r_low_conf = AgentResult(
            agent_type=AgentType.SENTIMENT,
            recommendation=RecommendationType.HOLD,
            score=RecommendationScore(Decimal("0.00")),
            confidence=ConfidenceScore(Decimal("0.40")),
            reasoning="Unclear social sentiment signals",
            evidence=[],
        )

    def test_evidence_aggregator(self) -> None:
        aggregator = EvidenceAggregator()
        ev_list = aggregator.aggregate_evidence([self.r_buy, self.r_sell, self.r_low_conf])
        self.assertEqual(len(ev_list), 2)

    def test_weighted_consensus_strategy(self) -> None:
        strategy = WeightedConsensusStrategy()
        score, rec, agreement, weights = strategy.compute_weighted_score([self.r_buy, self.r_sell])

        self.assertIsNotNone(score)
        self.assertIn(rec, list(RecommendationType))
        self.assertGreaterEqual(agreement, 0.0)
        self.assertIn("FUNDAMENTAL", weights)

    def test_conflict_detector(self) -> None:
        detector = ConflictDetector()
        conflicts = detector.detect_conflicts([self.r_buy, self.r_sell, self.r_low_conf])

        conflict_types = [c.conflict_type for c in conflicts]
        self.assertIn("BUY_VS_SELL", conflict_types)
        self.assertIn("MISSING_EVIDENCE", conflict_types)
        self.assertIn("LOW_CONFIDENCE", conflict_types)
        self.assertIn("CONFLICTING_ASSUMPTIONS", conflict_types)

    def test_confidence_engine_penalties(self) -> None:
        detector = ConflictDetector()
        conf_engine = ConfidenceEngine()

        conflicts = detector.detect_conflicts([self.r_buy, self.r_sell])
        composite_conf = conf_engine.compute_composite_confidence(
            [self.r_buy, self.r_sell], conflicts
        )

        # Baseline confidence is penalized due to BUY_VS_SELL high-severity conflict
        self.assertLess(float(composite_conf.value), 0.85)

    def test_decision_explainer_structured_output(self) -> None:
        explainer = DecisionExplainer()
        detector = ConflictDetector()
        conflicts = detector.detect_conflicts([self.r_buy, self.r_sell])

        explanation = explainer.explain(
            RecommendationType.BUY, [self.r_buy, self.r_sell], conflicts
        )

        self.assertIsInstance(explanation.key_drivers, list)
        self.assertIsInstance(explanation.identified_risks, list)
        self.assertIsInstance(explanation.critical_assumptions, list)
        self.assertIsInstance(explanation.unknowns_and_gaps, list)
        self.assertIn("PASSED_WITH_WARNINGS", explanation.policy_compliance_status)

    def test_audit_recorder_and_hash_signature(self) -> None:
        recorder = AuditRecorder()
        graph = recorder.build_reasoning_graph([self.r_buy], RecommendationType.BUY)

        self.assertGreater(len(graph.nodes), 0)
        self.assertGreater(len(graph.edges), 0)

        audit = recorder.record_audit(
            session_id="session-101",
            results=[self.r_buy],
            applied_weights={"FUNDAMENTAL": 1.2},
            conflict_count=0,
            final_recommendation=RecommendationType.BUY,
            consensus_score=0.80,
            confidence_score=0.85,
            agreement_score=1.0,
        )

        self.assertIsNotNone(audit.hash_signature)
        self.assertEqual(len(audit.hash_signature), 64)

    def test_consensus_engine_full_pipeline(self) -> None:
        decision = self.engine.evaluate_committee_decision(
            results=[self.r_buy, self.r_sell, self.r_low_conf],
            session_id="session-full-pipeline",
        )

        self.assertIsInstance(decision, ConsensusIntelligenceDecision)
        self.assertEqual(len(decision.evidence), 2)
        self.assertGreater(len(decision.conflicts), 0)
        self.assertIsNotNone(decision.explanation)
        self.assertIsNotNone(decision.reasoning_graph)
        self.assertIsNotNone(decision.audit_record)

        d_dict = decision.to_dict()
        self.assertIn("agreement_score", d_dict)
        self.assertIn("audit_record", d_dict)


if __name__ == "__main__":
    unittest.main()
