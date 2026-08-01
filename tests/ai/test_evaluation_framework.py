"""
Unit tests for AI Evaluation & Benchmarking Framework.
"""

import unittest
from decimal import Decimal

from packages.ai.evaluation import (
    CalibrationAnalyzer,
    DatasetManager,
    EvaluationEngine,
    EvaluationMetrics,
    Leaderboard,
    MetricsCalculator,
    ReportGenerator,
)
from packages.ai.models import AgentResult
from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


class TestAIEvaluationFramework(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = EvaluationEngine()
        self.dataset_manager = DatasetManager()
        self.metrics_calculator = MetricsCalculator()
        self.calibration_analyzer = CalibrationAnalyzer()
        self.leaderboard = Leaderboard()
        self.report_generator = ReportGenerator()

    def test_dataset_manager_defaults(self) -> None:
        ds_list = self.dataset_manager.list_datasets()
        self.assertGreater(len(ds_list), 0)

        nifty_ds = self.dataset_manager.get_dataset("nifty50-mock-v1")
        self.assertEqual(len(nifty_ds.samples), 5)
        self.assertEqual(nifty_ds.samples[0].ticker, "RELIANCE.NS")

    def test_metrics_calculator(self) -> None:
        preds = ["BUY", "SELL", "HOLD"]
        truths = ["BUY", "BUY", "HOLD"]
        acc = self.metrics_calculator.calculate_accuracy(preds, truths)
        self.assertAlmostEqual(acc, 2 / 3, places=2)

        j_rate = self.metrics_calculator.calculate_json_validation_rate([True, True, False])
        self.assertAlmostEqual(j_rate, 2 / 3, places=2)

        p_score = self.metrics_calculator.calculate_prompt_performance_score(
            accuracy=0.8, json_validation_rate=0.9, retry_rate=0.05
        )
        self.assertGreater(p_score, 0.70)

    def test_calibration_analyzer(self) -> None:
        confidences = [0.90, 0.80, 0.70, 0.60, 0.40]
        outcomes = [True, True, True, False, False]

        brier = self.calibration_analyzer.compute_brier_score(confidences, outcomes)
        self.assertGreaterEqual(brier, 0.0)
        self.assertLessEqual(brier, 1.0)

        ece = self.calibration_analyzer.compute_expected_calibration_error(confidences, outcomes)
        self.assertGreaterEqual(ece, 0.0)

    def test_leaderboard_ranking(self) -> None:
        self.leaderboard.add_or_update_entry(
            agent_name="FundamentalAgent",
            accuracy=0.85,
            json_validation_rate=0.95,
            avg_latency_ms=120.0,
            confidence_calibration=0.04,
        )

        self.leaderboard.add_or_update_entry(
            agent_name="RiskAgent",
            accuracy=0.70,
            json_validation_rate=0.80,
            avg_latency_ms=90.0,
            confidence_calibration=0.10,
        )

        ranked = self.leaderboard.get_ranked_leaderboard()
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0].agent_name, "FundamentalAgent")
        self.assertEqual(ranked[0].rank, 1)

    def test_report_generator(self) -> None:
        metrics = EvaluationMetrics(
            agent_accuracy=0.80,
            consensus_accuracy=0.85,
            prompt_performance_score=0.82,
            json_validation_rate=0.95,
            avg_latency_ms=115.0,
            retry_rate=0.02,
            expected_calibration_error=0.03,
            brier_score=0.05,
            total_evaluations=10,
        )

        ranked = self.leaderboard.get_ranked_leaderboard()
        json_rep = self.report_generator.generate_json_report(metrics, ranked)
        self.assertIn("metrics", json_rep)
        self.assertEqual(json_rep["metrics"]["agent_accuracy"], 0.80)

        md_rep = self.report_generator.generate_markdown_report(metrics, ranked)
        self.assertIn("# AI Core Benchmarking & Evaluation Report", md_rep)
        self.assertIn("80.0%", md_rep)

    def test_evaluation_engine_full_benchmark_suite(self) -> None:
        metrics, json_rep, md_rep = self.engine.run_benchmark_suite("nifty50-mock-v1")

        self.assertIsInstance(metrics, EvaluationMetrics)
        self.assertIsNotNone(json_rep)
        self.assertIsNotNone(md_rep)
        self.assertIn("FundamentalAgent", md_rep)

        # Check history retention
        history = self.engine.get_evaluation_history()
        self.assertGreater(len(history), 0)

    def test_backward_compatibility_evaluations(self) -> None:
        res = AgentResult(
            agent_type=AgentType.FUNDAMENTAL,
            recommendation=RecommendationType.BUY,
            score=RecommendationScore(Decimal("0.80")),
            confidence=ConfidenceScore(Decimal("0.85")),
            reasoning="Valid reasoning text",
        )
        report = self.engine.evaluate_result(res)
        self.assertTrue(report["is_compliant"])


if __name__ == "__main__":
    unittest.main()
