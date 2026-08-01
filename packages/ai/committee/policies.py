"""
Committee Execution Policies.

Defines default retries, timeout bounds, worker concurrency limits, and conflict penalty factors.
"""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class ExecutionPolicy:
    """Configurable execution parameters for CommitteeScheduler and CommitteePlanner."""

    max_parallel_workers: int = 4
    default_task_timeout_seconds: float = 30.0
    max_retries_per_task: int = 2
    retry_backoff_factor: float = 1.5
    allow_partial_failures: bool = True
    min_confidence_threshold: float = 0.50
    conflict_penalty_weight: float = 0.15
    token_budget_per_agent: int = 4096


@dataclass(frozen=True)
class AgentWeightPolicy:
    """Agent voting weights applied during committee consensus evaluation."""

    weights: dict[str, Decimal] = field(
        default_factory=lambda: {
            "FUNDAMENTAL": Decimal("1.2"),
            "QUANT": Decimal("1.0"),
            "SENTIMENT": Decimal("0.8"),
            "MACRO": Decimal("1.0"),
            "RISK": Decimal("1.3"),
        }
    )
