"""
Strategy Aggregate Root and StrategyVersion for the Indian AI Hedge Fund Domain.

Root entity encapsulating strategy metadata, versioning, signal generation, optimization runs,
and lifecycle status management. Pure domain entity with zero infrastructure dependencies.
"""

from dataclasses import dataclass, field
from typing import Any

from packages.domain.enums.strategy import SignalType, StrategyStatus, StrategyType
from packages.domain.exceptions import ValidationError
from packages.domain.strategy.optimization import Optimization
from packages.domain.strategy.signal import Signal
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import StrategyId
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, slots=True)
class StrategyVersion:
    """
    Immutable value object representing a specific versioned iteration of a strategy.

    Attributes:
        version_number (str): Version label (e.g., '1.0.0').
        parameters (Dict[str, Any]): Configured parameter dictionary.
        created_at (Timestamp): Creation timestamp (UTC).
        changelog (str): Description of changes in this version.
    """

    version_number: str
    parameters: dict[str, Any]
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    changelog: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))

        if not self.version_number.strip():
            raise ValidationError("StrategyVersion version_number cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize StrategyVersion to dictionary."""
        return {
            "version_number": self.version_number,
            "parameters": dict(self.parameters),
            "created_at": self.created_at.to_dict(),
            "changelog": self.changelog,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StrategyVersion":
        """Deserialize dictionary to StrategyVersion."""
        return cls(
            version_number=data["version_number"],
            parameters=dict(data["parameters"]),
            created_at=Timestamp.from_dict(data["created_at"]),
            changelog=data.get("changelog", ""),
        )


@dataclass
class Strategy:
    """
    Strategy Aggregate Root.

    Attributes:
        id (StrategyId): Unique strategy identifier.
        name (str): Strategy display name.
        strategy_type (StrategyType): Strategy archetype (MOMENTUM, STAT_ARB, PAIRS_TRADING, etc.).
        status (StrategyStatus): Operational status (DRAFT, BACKTESTING, ACTIVE, PAUSED, RETIRED).
        versions (List[StrategyVersion]): Historical strategy version releases.
        signals (List[Signal]): Generated signal ledger.
        optimizations (List[Optimization]): Parameter optimization runs.
        created_at (Timestamp): Creation timestamp (UTC).
        updated_at (Timestamp): Last update timestamp (UTC).
    """

    name: str
    strategy_type: StrategyType
    id: StrategyId = field(default_factory=StrategyId.generate)
    status: StrategyStatus = StrategyStatus.DRAFT
    versions: list[StrategyVersion] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    optimizations: list[Optimization] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.id, StrategyId):
            object.__setattr__(self, "id", StrategyId(self.id))
        if not isinstance(self.strategy_type, StrategyType):
            object.__setattr__(self, "strategy_type", StrategyType(self.strategy_type))
        if not isinstance(self.status, StrategyStatus):
            object.__setattr__(self, "status", StrategyStatus(self.status))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))
        if not isinstance(self.updated_at, Timestamp):
            object.__setattr__(self, "updated_at", Timestamp(self.updated_at))

        if not self.name.strip():
            raise ValidationError("Strategy name cannot be empty.")

    def add_version(self, version: StrategyVersion) -> None:
        """Add a new version release to the strategy."""
        self.versions.append(version)
        self._touch()

    def generate_signal(
        self,
        ticker: Ticker,
        signal_type: SignalType,
        score: ConfidenceScore,
        strength: RecommendationScore,
        reasoning: str = "",
    ) -> Signal:
        """
        Generate and record a new quantitative trade Signal.
        """
        signal = Signal(
            strategy_id=self.id,
            ticker=ticker,
            signal_type=signal_type,
            score=score,
            strength=strength,
            generated_at=Timestamp.now_utc(),
            reasoning=reasoning,
        )
        self.signals.append(signal)
        self._touch()
        return signal

    def record_optimization(self, optimization: Optimization) -> None:
        """Record an optimization run for this strategy."""
        self.optimizations.append(optimization)
        self._touch()

    def update_status(self, new_status: StrategyStatus) -> None:
        """Update operational status of the strategy."""
        object.__setattr__(self, "status", new_status)
        self._touch()

    def get_latest_version(self) -> StrategyVersion | None:
        """Return the latest deployed StrategyVersion if available."""
        return self.versions[-1] if self.versions else None

    def _touch(self) -> None:
        self.updated_at = Timestamp.now_utc()

    def to_dict(self) -> dict[str, Any]:
        """Serialize Strategy Aggregate Root to dictionary."""
        return {
            "id": self.id.to_dict(),
            "name": self.name,
            "strategy_type": self.strategy_type.value,
            "status": self.status.value,
            "versions": [v.to_dict() for v in self.versions],
            "signals": [s.to_dict() for s in self.signals],
            "optimizations": [o.to_dict() for o in self.optimizations],
            "created_at": self.created_at.to_dict(),
            "updated_at": self.updated_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Strategy":
        """Deserialize dictionary to Strategy Aggregate Root."""
        versions = [StrategyVersion.from_dict(v) for v in data.get("versions", [])]
        signals = [Signal.from_dict(s) for s in data.get("signals", [])]
        optimizations = [Optimization.from_dict(o) for o in data.get("optimizations", [])]

        return cls(
            id=StrategyId.from_dict(data["id"]),
            name=data["name"],
            strategy_type=StrategyType(data["strategy_type"]),
            status=StrategyStatus(data["status"]),
            versions=versions,
            signals=signals,
            optimizations=optimizations,
            created_at=Timestamp.from_dict(data["created_at"]),
            updated_at=Timestamp.from_dict(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Strategy):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
