"""
Consensus & Multi-Agent Voting Models for the Indian AI Hedge Fund Domain.

Provides AgentOpinion, AgentVote, ConsensusDecision, and FinalRecommendation models.
Pure domain models with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType
from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore


@dataclass(frozen=True, slots=True)
class AgentOpinion:
    """
    Immutable value object representing an individual AI Agent's analytical opinion.

    Attributes:
        agent_type (AgentType): Specialized agent role (QUANT, FUNDAMENTAL, RISK, etc.).
        recommendation (RecommendationType): Directional trade recommendation.
        reasoning (str): Textual justification/reasoning.
        confidence (ConfidenceScore): Confidence score [0, 1].
        supporting_evidence (List[str]): List of supporting data points.
        conflicting_evidence (List[str]): List of identified counter-arguments or risk factors.
    """

    agent_type: AgentType
    recommendation: RecommendationType
    reasoning: str
    confidence: ConfidenceScore
    supporting_evidence: list[str] = field(default_factory=list)
    conflicting_evidence: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.agent_type, AgentType):
            object.__setattr__(self, "agent_type", AgentType(self.agent_type))
        if not isinstance(self.recommendation, RecommendationType):
            object.__setattr__(self, "recommendation", RecommendationType(self.recommendation))
        if not isinstance(self.confidence, ConfidenceScore):
            object.__setattr__(self, "confidence", ConfidenceScore(to_decimal(self.confidence)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize AgentOpinion to dictionary."""
        return {
            "agent_type": self.agent_type.value,
            "recommendation": self.recommendation.value,
            "reasoning": self.reasoning,
            "confidence": self.confidence.to_dict(),
            "supporting_evidence": list(self.supporting_evidence),
            "conflicting_evidence": list(self.conflicting_evidence),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentOpinion":
        """Deserialize dictionary to AgentOpinion."""
        return cls(
            agent_type=AgentType(data["agent_type"]),
            recommendation=RecommendationType(data["recommendation"]),
            reasoning=data["reasoning"],
            confidence=ConfidenceScore.from_dict(data["confidence"]),
            supporting_evidence=data.get("supporting_evidence", []),
            conflicting_evidence=data.get("conflicting_evidence", []),
        )


@dataclass(frozen=True, slots=True)
class AgentVote:
    """
    Immutable value object representing an agent's vote in committee consensus.

    Attributes:
        agent_type (AgentType): Voting agent role.
        recommendation (RecommendationType): Cast vote recommendation.
        weight (Decimal): Voting weight multiplier (defaults to 1.0).
    """

    agent_type: AgentType
    recommendation: RecommendationType
    weight: Decimal = Decimal("1.0")

    def __post_init__(self) -> None:
        if not isinstance(self.agent_type, AgentType):
            object.__setattr__(self, "agent_type", AgentType(self.agent_type))
        if not isinstance(self.recommendation, RecommendationType):
            object.__setattr__(self, "recommendation", RecommendationType(self.recommendation))

        dec_w = to_decimal(self.weight)
        if dec_w <= Decimal("0"):
            raise ValidationError("AgentVote weight must be strictly positive.")
        object.__setattr__(self, "weight", dec_w)

    def to_dict(self) -> dict[str, Any]:
        """Serialize AgentVote to dictionary."""
        return {
            "agent_type": self.agent_type.value,
            "recommendation": self.recommendation.value,
            "weight": str(self.weight),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentVote":
        """Deserialize dictionary to AgentVote."""
        return cls(
            agent_type=AgentType(data["agent_type"]),
            recommendation=RecommendationType(data["recommendation"]),
            weight=Decimal(str(data.get("weight", "1.0"))),
        )


@dataclass
class ConsensusDecision:
    """
    ConsensusDecision Entity.

    Attributes:
        id (uuid.UUID): Unique consensus decision identifier.
        opinions (List[AgentOpinion]): Individual agent opinions collected.
        votes (List[AgentVote]): Weighted voting tally.
        consensus_score (RecommendationScore): Aggregated recommendation score [-1.0, 1.0].
        confidence (ConfidenceScore): Average agent confidence score [0, 1].
        summary (str): Executive consensus summary.
    """

    opinions: list[AgentOpinion]
    votes: list[AgentVote]
    consensus_score: RecommendationScore
    confidence: ConfidenceScore
    summary: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.consensus_score, RecommendationScore):
            object.__setattr__(
                self, "consensus_score", RecommendationScore(to_decimal(self.consensus_score))
            )
        if not isinstance(self.confidence, ConfidenceScore):
            object.__setattr__(self, "confidence", ConfidenceScore(to_decimal(self.confidence)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize ConsensusDecision to dictionary."""
        return {
            "id": str(self.id),
            "opinions": [o.to_dict() for o in self.opinions],
            "votes": [v.to_dict() for v in self.votes],
            "consensus_score": self.consensus_score.to_dict(),
            "confidence": self.confidence.to_dict(),
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConsensusDecision":
        """Deserialize dictionary to ConsensusDecision."""
        opinions = [AgentOpinion.from_dict(o) for o in data.get("opinions", [])]
        votes = [AgentVote.from_dict(v) for v in data.get("votes", [])]

        return cls(
            id=uuid.UUID(data["id"]),
            opinions=opinions,
            votes=votes,
            consensus_score=RecommendationScore.from_dict(data["consensus_score"]),
            confidence=ConfidenceScore.from_dict(data["confidence"]),
            summary=data.get("summary", ""),
        )


@dataclass(frozen=True, slots=True)
class FinalRecommendation:
    """
    Immutable value object representing the final investment committee recommendation.

    Attributes:
        recommendation (RecommendationType): Approved recommendation (STRONG_BUY, BUY, etc.).
        score (RecommendationScore): Final recommendation score [-1.0, 1.0].
        confidence (ConfidenceScore): Overall decision confidence [0, 1].
        rationale (str): Final executive investment rationale summary.
    """

    recommendation: RecommendationType
    score: RecommendationScore
    confidence: ConfidenceScore
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(self.recommendation, RecommendationType):
            object.__setattr__(self, "recommendation", RecommendationType(self.recommendation))
        if not isinstance(self.score, RecommendationScore):
            object.__setattr__(self, "score", RecommendationScore(to_decimal(self.score)))
        if not isinstance(self.confidence, ConfidenceScore):
            object.__setattr__(self, "confidence", ConfidenceScore(to_decimal(self.confidence)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize FinalRecommendation to dictionary."""
        return {
            "recommendation": self.recommendation.value,
            "score": self.score.to_dict(),
            "confidence": self.confidence.to_dict(),
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FinalRecommendation":
        """Deserialize dictionary to FinalRecommendation."""
        return cls(
            recommendation=RecommendationType(data["recommendation"]),
            score=RecommendationScore.from_dict(data["score"]),
            confidence=ConfidenceScore.from_dict(data["confidence"]),
            rationale=data.get("rationale", ""),
        )
