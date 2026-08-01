"""
Strategy Optimization Models for the Indian AI Hedge Fund Platform.

Provides Parameter, Constraint, ObjectiveFunction, EvaluationResult, and Optimization models.
Pure domain models with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.percentage import Percentage
from packages.domain.value_objects.identifiers.uuid_wrappers import StrategyId
from packages.domain.value_objects.metrics.ratios import Drawdown, SharpeRatio


@dataclass(frozen=True, slots=True)
class Parameter:
    """
    Immutable value object representing a strategy hyperparameter range.

    Attributes:
        name (str): Parameter name.
        value (Any): Current parameter value.
        min_value (Optional[Decimal]): Minimum search space boundary.
        max_value (Optional[Decimal]): Maximum search space boundary.
        step (Optional[Decimal]): Search step size increment.
    """

    name: str
    value: Any
    min_value: Decimal | None = None
    max_value: Decimal | None = None
    step: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize Parameter to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "min_value": str(self.min_value) if self.min_value is not None else None,
            "max_value": str(self.max_value) if self.max_value is not None else None,
            "step": str(self.step) if self.step is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Parameter":
        """Deserialize dictionary to Parameter."""
        return cls(
            name=data["name"],
            value=data["value"],
            min_value=Decimal(str(data["min_value"])) if data.get("min_value") else None,
            max_value=Decimal(str(data["max_value"])) if data.get("max_value") else None,
            step=Decimal(str(data["step"])) if data.get("step") else None,
        )


@dataclass(frozen=True, slots=True)
class Constraint:
    """
    Immutable value object representing an optimization search constraint.

    Attributes:
        name (str): Constraint name.
        constraint_type (str): Constraint type (MAX_DRAWDOWN, MIN_SHARPE, etc.).
        threshold (Decimal): Threshold value limit.
    """

    name: str
    constraint_type: str
    threshold: Decimal

    def __post_init__(self) -> None:
        dec_t = to_decimal(self.threshold)
        object.__setattr__(self, "threshold", dec_t)

    def is_satisfied(self, metric_value: Decimal) -> bool:
        """Return True if metric_value satisfies constraint threshold."""
        if "MAX" in self.constraint_type.upper():
            return metric_value <= self.threshold
        elif "MIN" in self.constraint_type.upper():
            return metric_value >= self.threshold
        return True

    def to_dict(self) -> dict[str, Any]:
        """Serialize Constraint to dictionary."""
        return {
            "name": self.name,
            "constraint_type": self.constraint_type,
            "threshold": str(self.threshold),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Constraint":
        """Deserialize dictionary to Constraint."""
        return cls(
            name=data["name"],
            constraint_type=data["constraint_type"],
            threshold=Decimal(str(data["threshold"])),
        )


@dataclass(frozen=True, slots=True)
class ObjectiveFunction:
    """
    Immutable value object representing the optimization target objective function.

    Attributes:
        metric_name (str): Metric to optimize (SHARPE_RATIO, CAGR, MIN_DRAWDOWN).
        maximize (bool): True if target should be maximized, False if minimized.
    """

    metric_name: str
    maximize: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize ObjectiveFunction to dictionary."""
        return {
            "metric_name": self.metric_name,
            "maximize": self.maximize,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObjectiveFunction":
        """Deserialize dictionary to ObjectiveFunction."""
        return cls(
            metric_name=data["metric_name"],
            maximize=data.get("maximize", True),
        )


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """
    Immutable value object representing a single parameter set evaluation trial result.

    Attributes:
        parameters (Dict[str, Any]): Evaluated parameter combination.
        sharpe_ratio (SharpeRatio): Evaluated Sharpe ratio.
        cagr (Percentage): Evaluated CAGR percentage return.
        max_drawdown (Drawdown): Evaluated maximum drawdown.
        score (Decimal): Calculated objective score.
    """

    parameters: dict[str, Any]
    sharpe_ratio: SharpeRatio
    cagr: Percentage
    max_drawdown: Drawdown
    score: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.sharpe_ratio, SharpeRatio):
            object.__setattr__(self, "sharpe_ratio", SharpeRatio(to_decimal(self.sharpe_ratio)))
        if not isinstance(self.cagr, Percentage):
            object.__setattr__(self, "cagr", Percentage(to_decimal(self.cagr)))
        if not isinstance(self.max_drawdown, Drawdown):
            object.__setattr__(self, "max_drawdown", Drawdown.from_value(self.max_drawdown))
        object.__setattr__(self, "score", to_decimal(self.score))

    def to_dict(self) -> dict[str, Any]:
        """Serialize EvaluationResult to dictionary."""
        return {
            "parameters": dict(self.parameters),
            "sharpe_ratio": self.sharpe_ratio.to_dict(),
            "cagr": self.cagr.to_dict(),
            "max_drawdown": self.max_drawdown.to_dict(),
            "score": str(self.score),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationResult":
        """Deserialize dictionary to EvaluationResult."""
        return cls(
            parameters=dict(data["parameters"]),
            sharpe_ratio=SharpeRatio.from_dict(data["sharpe_ratio"]),
            cagr=Percentage.from_dict(data["cagr"]),
            max_drawdown=Drawdown.from_dict(data["max_drawdown"]),
            score=Decimal(str(data["score"])),
        )


@dataclass
class Optimization:
    """
    Optimization Entity.

    Attributes:
        id (uuid.UUID): Unique optimization run identifier.
        strategy_id (StrategyId): Target strategy ID.
        objective (ObjectiveFunction): Optimization objective target.
        parameters (List[Parameter]): Parameter search grid/space.
        constraints (List[Constraint]): Evaluation constraints.
        results (List[EvaluationResult]): Evaluation trials.
        best_result (Optional[EvaluationResult]): Optimal parameter trial result.
    """

    strategy_id: StrategyId
    objective: ObjectiveFunction
    parameters: list[Parameter] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    results: list[EvaluationResult] = field(default_factory=list)
    best_result: EvaluationResult | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.strategy_id, StrategyId):
            object.__setattr__(self, "strategy_id", StrategyId(self.strategy_id))

    def add_result(self, result: EvaluationResult) -> None:
        """Add an evaluation result trial and update best_result if optimal."""
        self.results.append(result)

        if self.best_result is None:
            self.best_result = result
        else:
            if self.objective.maximize:
                if result.score > self.best_result.score:
                    self.best_result = result
            else:
                if result.score < self.best_result.score:
                    self.best_result = result

    def to_dict(self) -> dict[str, Any]:
        """Serialize Optimization to dictionary."""
        return {
            "id": str(self.id),
            "strategy_id": self.strategy_id.to_dict(),
            "objective": self.objective.to_dict(),
            "parameters": [p.to_dict() for p in self.parameters],
            "constraints": [c.to_dict() for c in self.constraints],
            "results": [r.to_dict() for r in self.results],
            "best_result": self.best_result.to_dict() if self.best_result else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Optimization":
        """Deserialize dictionary to Optimization."""
        params = [Parameter.from_dict(p) for p in data.get("parameters", [])]
        consts = [Constraint.from_dict(c) for c in data.get("constraints", [])]
        res = [EvaluationResult.from_dict(r) for r in data.get("results", [])]
        best_r = (
            EvaluationResult.from_dict(data["best_result"]) if data.get("best_result") else None
        )

        return cls(
            id=uuid.UUID(data["id"]),
            strategy_id=StrategyId.from_dict(data["strategy_id"]),
            objective=ObjectiveFunction.from_dict(data["objective"]),
            parameters=params,
            constraints=consts,
            results=res,
            best_result=best_r,
        )
