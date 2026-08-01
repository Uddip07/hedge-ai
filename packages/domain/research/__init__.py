"""
Research Domain Package for the Indian AI Hedge Fund Platform.

Consolidates ResearchReport Aggregate Root, FundamentalAnalysis, TechnicalAnalysis,
MacroAnalysis, SentimentAnalysis, AgentOpinion, AgentVote, ConsensusDecision, and FinalRecommendation.
"""

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
from packages.domain.research.report import ResearchReport

__all__ = [
    "ResearchReport",
    "FundamentalAnalysis",
    "TechnicalAnalysis",
    "MacroAnalysis",
    "SentimentAnalysis",
    "AgentOpinion",
    "AgentVote",
    "ConsensusDecision",
    "FinalRecommendation",
]
