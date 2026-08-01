"""
Backtest Aggregate Root and BacktestRun Domain Models for the Indian AI Hedge Fund Platform.

Root entity managing historical simulation parameters, run history, and evaluation outputs.
Pure domain entity with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.backtesting.metrics import BacktestResult
from packages.domain.exceptions import EntityNotFoundError, ValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import BacktestId, StrategyId
from packages.domain.value_objects.temporal.timestamps import Timestamp, TradingDate


@dataclass
class BacktestRun:
    """
    BacktestRun Entity representing a single simulation execution attempt.

    Attributes:
        run_id (uuid.UUID): Unique run identifier.
        run_number (int): Sequential run iteration number.
        started_at (Timestamp): Simulation start timestamp (UTC).
        completed_at (Optional[Timestamp]): Simulation completion timestamp (UTC).
        status (str): Execution status (RUNNING, COMPLETED, FAILED).
        result (Optional[BacktestResult]): Simulation result payload upon completion.
    """

    run_number: int
    run_id: uuid.UUID = field(default_factory=uuid.uuid4)
    started_at: Timestamp = field(default_factory=Timestamp.now_utc)
    completed_at: Timestamp | None = None
    status: str = "RUNNING"
    result: BacktestResult | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.started_at, Timestamp):
            object.__setattr__(self, "started_at", Timestamp(self.started_at))
        if self.completed_at is not None and not isinstance(self.completed_at, Timestamp):
            object.__setattr__(self, "completed_at", Timestamp(self.completed_at))

    def complete(self, result: BacktestResult) -> None:
        """Mark run completed with result payload."""
        object.__setattr__(self, "result", result)
        object.__setattr__(self, "status", "COMPLETED")
        object.__setattr__(self, "completed_at", Timestamp.now_utc())

    def fail(self) -> None:
        """Mark run failed."""
        object.__setattr__(self, "status", "FAILED")
        object.__setattr__(self, "completed_at", Timestamp.now_utc())

    def to_dict(self) -> dict[str, Any]:
        """Serialize BacktestRun to dictionary."""
        return {
            "run_id": str(self.run_id),
            "run_number": self.run_number,
            "started_at": self.started_at.to_dict(),
            "completed_at": self.completed_at.to_dict() if self.completed_at else None,
            "status": self.status,
            "result": self.result.to_dict() if self.result else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BacktestRun":
        """Deserialize dictionary to BacktestRun."""
        res_obj = BacktestResult.from_dict(data["result"]) if data.get("result") else None
        comp_t = Timestamp.from_dict(data["completed_at"]) if data.get("completed_at") else None

        return cls(
            run_id=uuid.UUID(data["run_id"]),
            run_number=int(data["run_number"]),
            started_at=Timestamp.from_dict(data["started_at"]),
            completed_at=comp_t,
            status=data.get("status", "RUNNING"),
            result=res_obj,
        )


@dataclass
class Backtest:
    """
    Backtest Aggregate Root.

    Attributes:
        id (BacktestId): Unique backtest configuration identifier.
        strategy_id (StrategyId): Target strategy ID being evaluated.
        name (str): Backtest configuration name.
        start_date (TradingDate): Historical start trading date.
        end_date (TradingDate): Historical end trading date.
        initial_capital (Money): Starting simulated equity capital.
        benchmark_ticker (Optional[Ticker]): Benchmark asset ticker (e.g. NIFTY50.NSE).
        runs (List[BacktestRun]): Tracked simulation run attempts.
        created_at (Timestamp): Creation timestamp (UTC).
        updated_at (Timestamp): Last update timestamp (UTC).
    """

    strategy_id: StrategyId
    name: str
    start_date: TradingDate
    end_date: TradingDate
    initial_capital: Money
    id: BacktestId = field(default_factory=BacktestId.generate)
    benchmark_ticker: Ticker | None = None
    runs: list[BacktestRun] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.id, BacktestId):
            object.__setattr__(self, "id", BacktestId(self.id))
        if not isinstance(self.strategy_id, StrategyId):
            object.__setattr__(self, "strategy_id", StrategyId(self.strategy_id))
        if not isinstance(self.start_date, TradingDate):
            object.__setattr__(self, "start_date", TradingDate(self.start_date))
        if not isinstance(self.end_date, TradingDate):
            object.__setattr__(self, "end_date", TradingDate(self.end_date))
        if not isinstance(self.initial_capital, Money):
            object.__setattr__(self, "initial_capital", Money(self.initial_capital))
        if self.benchmark_ticker is not None and not isinstance(self.benchmark_ticker, Ticker):
            object.__setattr__(self, "benchmark_ticker", Ticker(self.benchmark_ticker))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))
        if not isinstance(self.updated_at, Timestamp):
            object.__setattr__(self, "updated_at", Timestamp(self.updated_at))

        if self.start_date.value >= self.end_date.value:
            raise ValidationError("Backtest start_date must be strictly before end_date.")
        if not self.name.strip():
            raise ValidationError("Backtest name cannot be empty.")

    def start_run(self) -> BacktestRun:
        """Initiate and record a new BacktestRun attempt."""
        run_number = len(self.runs) + 1
        new_run = BacktestRun(run_number=run_number, started_at=Timestamp.now_utc())
        self.runs.append(new_run)
        self._touch()
        return new_run

    def complete_run(self, run_id: uuid.UUID, result: BacktestResult) -> None:
        """
        Mark a specific BacktestRun completed with results.

        Raises:
            EntityNotFoundError: If run_id is not found.
        """
        for run in self.runs:
            if run.run_id == run_id:
                run.complete(result)
                self._touch()
                return

        raise EntityNotFoundError(
            f"BacktestRun '{run_id}' not found in backtest '{self.name}'.",
            context={"backtest": self.name, "run_id": str(run_id)},
        )

    def get_latest_result(self) -> BacktestResult | None:
        """Return the completed BacktestResult from the most recent completed run."""
        for run in reversed(self.runs):
            if run.status == "COMPLETED" and run.result is not None:
                return run.result
        return None

    def _touch(self) -> None:
        self.updated_at = Timestamp.now_utc()

    def to_dict(self) -> dict[str, Any]:
        """Serialize Backtest Aggregate Root to dictionary."""
        return {
            "id": self.id.to_dict(),
            "strategy_id": self.strategy_id.to_dict(),
            "name": self.name,
            "start_date": self.start_date.to_dict(),
            "end_date": self.end_date.to_dict(),
            "initial_capital": self.initial_capital.to_dict(),
            "benchmark_ticker": self.benchmark_ticker.to_dict() if self.benchmark_ticker else None,
            "runs": [r.to_dict() for r in self.runs],
            "created_at": self.created_at.to_dict(),
            "updated_at": self.updated_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Backtest":
        """Deserialize dictionary to Backtest Aggregate Root."""
        runs = [BacktestRun.from_dict(r) for r in data.get("runs", [])]
        bench_obj = (
            Ticker.from_dict(data["benchmark_ticker"]) if data.get("benchmark_ticker") else None
        )

        return cls(
            id=BacktestId.from_dict(data["id"]),
            strategy_id=StrategyId.from_dict(data["strategy_id"]),
            name=data["name"],
            start_date=TradingDate.from_dict(data["start_date"]),
            end_date=TradingDate.from_dict(data["end_date"]),
            initial_capital=Money.from_dict(data["initial_capital"]),
            benchmark_ticker=bench_obj,
            runs=runs,
            created_at=Timestamp.from_dict(data["created_at"]),
            updated_at=Timestamp.from_dict(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Backtest):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
