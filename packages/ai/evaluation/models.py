"""
Data Models for AI Evaluation & Benchmarking Framework.

Defines BenchmarkSample, BenchmarkDataset, EvaluationMetrics, and AgentLeaderboardEntry data structures.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class BenchmarkSample:
    """
    Individual benchmark sample containing ground truth target and metadata.

    Attributes:
        sample_id (str): Unique sample identifier.
        ticker (str): Target stock ticker symbol.
        ground_truth_recommendation (str): Expected trade recommendation (BUY, SELL, HOLD, etc.).
        expected_score_min (float): Lower bound for expected recommendation score.
        expected_score_max (float): Upper bound for expected recommendation score.
        metadata (dict[str, Any]): Additional context metadata.
    """

    sample_id: str
    ticker: str
    ground_truth_recommendation: str
    expected_score_min: float = -1.0
    expected_score_max: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "ticker": self.ticker,
            "ground_truth_recommendation": self.ground_truth_recommendation,
            "expected_score_min": self.expected_score_min,
            "expected_score_max": self.expected_score_max,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class BenchmarkDataset:
    """
    Collection of BenchmarkSamples representing a standard benchmarking test suite.
    """

    dataset_id: str
    name: str
    description: str
    samples: list[BenchmarkSample] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "description": self.description,
            "sample_count": len(self.samples),
            "samples": [s.to_dict() for s in self.samples],
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class EvaluationMetrics:
    """
    Comprehensive aggregated evaluation metrics.
    """

    agent_accuracy: float
    consensus_accuracy: float
    prompt_performance_score: float
    json_validation_rate: float
    avg_latency_ms: float
    retry_rate: float
    expected_calibration_error: float
    brier_score: float
    total_evaluations: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_accuracy": round(self.agent_accuracy, 4),
            "consensus_accuracy": round(self.consensus_accuracy, 4),
            "prompt_performance_score": round(self.prompt_performance_score, 4),
            "json_validation_rate": round(self.json_validation_rate, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "retry_rate": round(self.retry_rate, 4),
            "expected_calibration_error": round(self.expected_calibration_error, 4),
            "brier_score": round(self.brier_score, 4),
            "total_evaluations": self.total_evaluations,
        }


@dataclass(frozen=True)
class AgentLeaderboardEntry:
    """
    Leaderboard entry summarizing performance metrics for a specific agent role or model.
    """

    agent_name: str
    accuracy: float
    json_validation_rate: float
    avg_latency_ms: float
    confidence_calibration: float
    rank: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "accuracy": round(self.accuracy, 4),
            "json_validation_rate": round(self.json_validation_rate, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "confidence_calibration": round(self.confidence_calibration, 4),
            "rank": self.rank,
        }
