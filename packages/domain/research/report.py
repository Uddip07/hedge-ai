"""
ResearchReport Aggregate Root for the Indian AI Hedge Fund Domain.

Root entity encapsulating Fundamental Analysis, Technical Analysis, Macro Analysis,
Sentiment Analysis, Multi-Agent Consensus Decisions, and Final Investment Committee Recommendations.
Pure domain entity with zero infrastructure dependencies.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.research import ResearchStatus
from packages.domain.exceptions import ValidationError
from packages.domain.research.analyses import (
    FundamentalAnalysis,
    MacroAnalysis,
    SentimentAnalysis,
    TechnicalAnalysis,
)
from packages.domain.research.consensus import (
    AgentOpinion,
    AgentVote,
    ConsensusDecision,
    FinalRecommendation,
)
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.domain.value_objects.metrics.scores import ConfidenceScore, RecommendationScore
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class ResearchReport:
    """
    ResearchReport Aggregate Root.

    Attributes:
        id (ResearchId): Unique research report identifier.
        ticker (Ticker): Target asset ticker symbol.
        status (ResearchStatus): Report lifecycle status (DRAFT, IN_PROGRESS, COMPLETED, APPROVED, REJECTED).
        fundamental_analysis (Optional[FundamentalAnalysis]): Fundamental analysis module payload.
        technical_analysis (Optional[TechnicalAnalysis]): Technical analysis module payload.
        macro_analysis (Optional[MacroAnalysis]): Macroeconomic analysis module payload.
        sentiment_analysis (Optional[SentimentAnalysis]): News/social sentiment analysis payload.
        consensus (Optional[ConsensusDecision]): Multi-agent consensus decision.
        final_recommendation (Optional[FinalRecommendation]): Approved final investment recommendation.
        created_at (Timestamp): Creation timestamp (UTC).
        updated_at (Timestamp): Last update timestamp (UTC).
    """

    ticker: Ticker
    id: ResearchId = field(default_factory=ResearchId.generate)
    status: ResearchStatus = ResearchStatus.DRAFT
    fundamental_analysis: FundamentalAnalysis | None = None
    technical_analysis: TechnicalAnalysis | None = None
    macro_analysis: MacroAnalysis | None = None
    sentiment_analysis: SentimentAnalysis | None = None
    consensus: ConsensusDecision | None = None
    final_recommendation: FinalRecommendation | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.id, ResearchId):
            object.__setattr__(self, "id", ResearchId(self.id))
        if not isinstance(self.ticker, Ticker):
            object.__setattr__(self, "ticker", Ticker(self.ticker))
        if not isinstance(self.status, ResearchStatus):
            object.__setattr__(self, "status", ResearchStatus(self.status))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))
        if not isinstance(self.updated_at, Timestamp):
            object.__setattr__(self, "updated_at", Timestamp(self.updated_at))

    def update_fundamental(self, analysis: FundamentalAnalysis) -> None:
        """Update fundamental analysis payload."""
        object.__setattr__(self, "fundamental_analysis", analysis)
        self._touch()

    def update_technical(self, analysis: TechnicalAnalysis) -> None:
        """Update technical analysis payload."""
        object.__setattr__(self, "technical_analysis", analysis)
        self._touch()

    def update_macro(self, analysis: MacroAnalysis) -> None:
        """Update macro analysis payload."""
        object.__setattr__(self, "macro_analysis", analysis)
        self._touch()

    def update_sentiment(self, analysis: SentimentAnalysis) -> None:
        """Update sentiment analysis payload."""
        object.__setattr__(self, "sentiment_analysis", analysis)
        self._touch()

    def finalize_consensus(self, opinions: list[AgentOpinion]) -> ConsensusDecision:
        """
        Aggregate agent opinions, calculate weighted consensus decision score, and store consensus.
        """
        if not opinions:
            raise ValidationError("Cannot finalize consensus with zero agent opinions.")

        votes: list[AgentVote] = []
        total_score = Decimal("0.0")
        total_confidence = Decimal("0.0")

        for op in opinions:
            vote = AgentVote(
                agent_type=op.agent_type, recommendation=op.recommendation, weight=Decimal("1.0")
            )
            votes.append(vote)

            # Map recommendation score [+2..-2] normalized to [-1.0, 1.0]
            rec_multiplier = Decimal(str(op.recommendation.score())) / Decimal("2.0")
            total_score += rec_multiplier * op.confidence.value
            total_confidence += op.confidence.value

        count_dec = Decimal(str(len(opinions)))
        avg_score = (
            (total_score / total_confidence) if total_confidence > Decimal("0") else Decimal("0.0")
        )
        avg_conf = total_confidence / count_dec

        consensus_dec = ConsensusDecision(
            opinions=opinions,
            votes=votes,
            consensus_score=RecommendationScore(avg_score),
            confidence=ConfidenceScore(avg_conf),
            summary=f"Consensus derived from {len(opinions)} specialized research agents.",
        )

        object.__setattr__(self, "consensus", consensus_dec)
        object.__setattr__(self, "status", ResearchStatus.COMPLETED)
        self._touch()
        return consensus_dec

    def approve_report(self, final_rec: FinalRecommendation) -> None:
        """Approve research report and assign final investment committee recommendation."""
        object.__setattr__(self, "final_recommendation", final_rec)
        object.__setattr__(self, "status", ResearchStatus.APPROVED)
        self._touch()

    def _touch(self) -> None:
        object.__setattr__(self, "updated_at", Timestamp.now_utc())

    def to_dict(self) -> dict[str, Any]:
        """Serialize ResearchReport Aggregate Root to dictionary."""
        return {
            "id": self.id.to_dict(),
            "ticker": self.ticker.to_dict(),
            "status": self.status.value,
            "fundamental_analysis": (
                self.fundamental_analysis.to_dict() if self.fundamental_analysis else None
            ),
            "technical_analysis": (
                self.technical_analysis.to_dict() if self.technical_analysis else None
            ),
            "macro_analysis": self.macro_analysis.to_dict() if self.macro_analysis else None,
            "sentiment_analysis": (
                self.sentiment_analysis.to_dict() if self.sentiment_analysis else None
            ),
            "consensus": self.consensus.to_dict() if self.consensus else None,
            "final_recommendation": (
                self.final_recommendation.to_dict() if self.final_recommendation else None
            ),
            "created_at": self.created_at.to_dict(),
            "updated_at": self.updated_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchReport":
        """Deserialize dictionary to ResearchReport Aggregate Root."""
        fund = (
            FundamentalAnalysis.from_dict(data["fundamental_analysis"])
            if data.get("fundamental_analysis")
            else None
        )
        tech = (
            TechnicalAnalysis.from_dict(data["technical_analysis"])
            if data.get("technical_analysis")
            else None
        )
        macro = (
            MacroAnalysis.from_dict(data["macro_analysis"]) if data.get("macro_analysis") else None
        )
        sent = (
            SentimentAnalysis.from_dict(data["sentiment_analysis"])
            if data.get("sentiment_analysis")
            else None
        )
        cons = ConsensusDecision.from_dict(data["consensus"]) if data.get("consensus") else None
        f_rec = (
            FinalRecommendation.from_dict(data["final_recommendation"])
            if data.get("final_recommendation")
            else None
        )

        return cls(
            id=ResearchId.from_dict(data["id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            status=ResearchStatus(data["status"]),
            fundamental_analysis=fund,
            technical_analysis=tech,
            macro_analysis=macro,
            sentiment_analysis=sent,
            consensus=cons,
            final_recommendation=f_rec,
            created_at=Timestamp.from_dict(data["created_at"]),
            updated_at=Timestamp.from_dict(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ResearchReport):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
