"""
Evaluation Engine for AI Evaluation & Benchmarking Framework.

Central orchestrator for agent evaluation, dataset benchmarking, leaderboard management, and report generation.
"""

from typing import Any

from packages.ai.consensus.engine import ConsensusEngine
from packages.ai.evaluation.benchmark import BenchmarkRunner
from packages.ai.evaluation.calibration import CalibrationAnalyzer
from packages.ai.evaluation.datasets import DatasetManager
from packages.ai.evaluation.leaderboard import Leaderboard
from packages.ai.evaluation.metrics import MetricsCalculator
from packages.ai.evaluation.models import EvaluationMetrics
from packages.ai.evaluation.reports import ReportGenerator
from packages.ai.models.agent_result import AgentResult
from packages.ai.orchestrator import AgentOrchestrator
from packages.domain.research.consensus import ConsensusDecision


class EvaluationEngine:
    """
    Central Evaluation & Benchmarking Engine for AI Core Framework.
    """

    def __init__(
        self,
        dataset_manager: DatasetManager | None = None,
        metrics_calculator: MetricsCalculator | None = None,
        calibration_analyzer: CalibrationAnalyzer | None = None,
        report_generator: ReportGenerator | None = None,
        leaderboard: Leaderboard | None = None,
        benchmark_runner: BenchmarkRunner | None = None,
    ) -> None:
        self.dataset_manager = dataset_manager or DatasetManager()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        self.calibration_analyzer = calibration_analyzer or CalibrationAnalyzer()
        self.report_generator = report_generator or ReportGenerator()
        self.leaderboard = leaderboard or Leaderboard()
        self.benchmark_runner = benchmark_runner or BenchmarkRunner(
            dataset_manager=self.dataset_manager,
            metrics_calculator=self.metrics_calculator,
            calibration_analyzer=self.calibration_analyzer,
        )

        self._history: list[dict[str, Any]] = []

    def evaluate_result(self, result: AgentResult) -> dict[str, Any]:
        """
        Evaluate a single AgentResult payload (backward compatible).
        """
        is_valid_score = -1.0 <= float(result.score.value) <= 1.0
        is_valid_confidence = 0.0 <= float(result.confidence.value) <= 1.0
        has_reasoning = bool(result.reasoning and result.reasoning.strip())

        report = {
            "agent_type": result.agent_type.value,
            "is_valid_score": is_valid_score,
            "is_valid_confidence": is_valid_confidence,
            "has_reasoning": has_reasoning,
            "evidence_count": len(result.evidence),
            "is_compliant": is_valid_score and is_valid_confidence and has_reasoning,
        }
        self._history.append(report)
        return report

    def evaluate_consensus(self, consensus: ConsensusDecision) -> dict[str, Any]:
        """
        Evaluate a ConsensusDecision payload (backward compatible).
        """
        report = {
            "opinions_count": len(consensus.opinions),
            "votes_count": len(consensus.votes),
            "consensus_score": float(consensus.consensus_score.value),
            "confidence": float(consensus.confidence.value),
            "is_valid": len(consensus.opinions) > 0,
        }
        self._history.append(report)
        return report

    def run_benchmark_suite(
        self,
        dataset_id: str = "nifty50-mock-v1",
        orchestrator: AgentOrchestrator | None = None,
        consensus_engine: ConsensusEngine | None = None,
    ) -> tuple[EvaluationMetrics, dict[str, Any], str]:
        """
        Execute full benchmark suite and return metrics object, JSON report dict, and Markdown report string.
        """
        metrics = self.benchmark_runner.run_benchmark(
            dataset_id=dataset_id,
            orchestrator=orchestrator,
            consensus_engine=consensus_engine,
        )

        # Update leaderboard entries
        self.leaderboard.add_or_update_entry(
            agent_name="FundamentalAgent",
            accuracy=metrics.agent_accuracy,
            json_validation_rate=metrics.json_validation_rate,
            avg_latency_ms=metrics.avg_latency_ms,
            confidence_calibration=metrics.expected_calibration_error,
        )

        ranked_board = self.leaderboard.get_ranked_leaderboard()
        json_report = self.report_generator.generate_json_report(
            metrics=metrics,
            leaderboard=ranked_board,
            extra_metadata={"dataset_id": dataset_id},
        )

        markdown_report = self.report_generator.generate_markdown_report(
            metrics=metrics,
            leaderboard=ranked_board,
        )

        self._history.append(json_report)

        return metrics, json_report, markdown_report

    def get_evaluation_history(self) -> list[dict[str, Any]]:
        """Retrieve stored evaluation run history."""
        return list(self._history)
