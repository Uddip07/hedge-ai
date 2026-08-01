"""
Research Domain Events for the Indian AI Hedge Fund Platform.

Event definitions for research report creation, multi-agent consensus decisions, and report approvals.
"""

import uuid
from dataclasses import dataclass
from typing import Any

from packages.domain.enums.research import RecommendationType
from packages.domain.events.base import DomainEvent
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.domain.value_objects.metrics.scores import RecommendationScore
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class ResearchReportCreatedEvent(DomainEvent):
    """
    Emitted when a new research report thesis is created.
    """

    report_id: ResearchId
    ticker: Ticker

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "report_id": self.report_id.to_dict(),
                "ticker": self.ticker.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchReportCreatedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            report_id=ResearchId.from_dict(data["report_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
        )


@dataclass(frozen=True, kw_only=True)
class ConsensusReachedEvent(DomainEvent):
    """
    Emitted when multi-agent committee research arrives at a consensus decision.
    """

    report_id: ResearchId
    ticker: Ticker
    consensus_score: RecommendationScore

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "report_id": self.report_id.to_dict(),
                "ticker": self.ticker.to_dict(),
                "consensus_score": self.consensus_score.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConsensusReachedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            report_id=ResearchId.from_dict(data["report_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            consensus_score=RecommendationScore.from_dict(data["consensus_score"]),
        )


@dataclass(frozen=True, kw_only=True)
class ResearchReportApprovedEvent(DomainEvent):
    """
    Emitted when an investment committee approves a research report for execution.
    """

    report_id: ResearchId
    ticker: Ticker
    recommendation: RecommendationType

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "report_id": self.report_id.to_dict(),
                "ticker": self.ticker.to_dict(),
                "recommendation": self.recommendation.value,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchReportApprovedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            report_id=ResearchId.from_dict(data["report_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            recommendation=RecommendationType(data["recommendation"]),
        )
