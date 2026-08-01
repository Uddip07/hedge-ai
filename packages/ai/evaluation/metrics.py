"""
Metrics Calculator for AI Evaluation & Benchmarking Framework.

Computes accuracy, JSON schema validation rate, latency, retry rate, and prompt performance scores.
"""

from packages.ai.evaluation.models import EvaluationMetrics


class MetricsCalculator:
    """
    Calculator evaluating numerical performance metrics.
    """

    def calculate_accuracy(self, predictions: list[str], ground_truths: list[str]) -> float:
        """Calculate fraction of predictions matching ground truth targets exactly."""
        if not predictions or len(predictions) != len(ground_truths):
            return 0.0
        matches = sum(
            1 for p, g in zip(predictions, ground_truths, strict=False) if p.upper() == g.upper()
        )
        return matches / len(predictions)

    def calculate_json_validation_rate(self, validation_results: list[bool]) -> float:
        """Calculate percentage of model outputs passing JSON schema validation."""
        if not validation_results:
            return 1.0
        return sum(1 for v in validation_results if v) / len(validation_results)

    def calculate_prompt_performance_score(
        self,
        accuracy: float,
        json_validation_rate: float,
        retry_rate: float,
    ) -> float:
        """
        Compute composite prompt performance score [0, 1].
        Formula: 0.5 * accuracy + 0.4 * json_validation_rate - 0.1 * retry_rate
        """
        raw_score = (0.5 * accuracy) + (0.4 * json_validation_rate) - (0.1 * retry_rate)
        return max(0.0, min(1.0, raw_score))

    def compute_aggregate_metrics(
        self,
        agent_predictions: list[str],
        agent_ground_truths: list[str],
        consensus_predictions: list[str],
        consensus_ground_truths: list[str],
        json_validations: list[bool],
        latencies_ms: list[float],
        retries_count: int,
        total_calls: int,
        ece: float = 0.05,
        brier: float = 0.08,
    ) -> EvaluationMetrics:
        """
        Compute full EvaluationMetrics dataclass object.
        """
        a_acc = self.calculate_accuracy(agent_predictions, agent_ground_truths)
        c_acc = self.calculate_accuracy(consensus_predictions, consensus_ground_truths)
        j_rate = self.calculate_json_validation_rate(json_validations)

        r_rate = (retries_count / total_calls) if total_calls > 0 else 0.0
        avg_lat = (sum(latencies_ms) / len(latencies_ms)) if latencies_ms else 0.0

        p_score = self.calculate_prompt_performance_score(
            accuracy=a_acc,
            json_validation_rate=j_rate,
            retry_rate=r_rate,
        )

        return EvaluationMetrics(
            agent_accuracy=a_acc,
            consensus_accuracy=c_acc,
            prompt_performance_score=p_score,
            json_validation_rate=j_rate,
            avg_latency_ms=avg_lat,
            retry_rate=r_rate,
            expected_calibration_error=ece,
            brier_score=brier,
            total_evaluations=len(agent_predictions),
        )
