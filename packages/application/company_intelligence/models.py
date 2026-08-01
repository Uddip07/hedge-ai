"""
Data Models and Data Transfer Objects for Company Intelligence Context.

Defines input context, Intermediate State, Report Sections, Source Attributions,
Explainability models, and the complete ResearchReport structure.
"""

import json
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.market import ExchangeType, Timeframe
from packages.domain.enums.research import RecommendationType
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True)
class CompanyIntelligenceContext:
    """
    Input context for Company Intelligence workflow execution.

    Attributes:
        ticker (Ticker): Normalized target asset ticker symbol.
        session_id (str): Unique analysis session ID.
        parameters (dict[str, Any]): Workflow parameters (horizon, risk tolerance, etc.).
        metadata (dict[str, Any]): Execution metadata.
    """

    ticker: Ticker
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceAttribution:
    """Factual document source attribution metadata."""

    document_id: str
    company: str
    filing_type: str
    section: str
    page: int
    publication_date: str
    snippet: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "company": self.company,
            "filing_type": self.filing_type,
            "section": self.section,
            "page": self.page,
            "publication_date": self.publication_date,
            "snippet": self.snippet,
        }


@dataclass(frozen=True)
class SupportingEvidence:
    """Supporting factual evidence item with source attributions."""

    fact: str
    confidence_score: float
    citations: list[SourceAttribution] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact": self.fact,
            "confidence_score": self.confidence_score,
            "citations": [c.to_dict() for c in self.citations],
        }


@dataclass(frozen=True)
class MarketSnapshot:
    """Market price & exchange operational status snapshot."""

    ticker: str
    price: Price
    change_percent: Decimal
    volume: Decimal
    exchange: ExchangeType
    is_market_open: bool
    timestamp: Timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "price": str(self.price.amount),
            "currency": str(self.price.money.currency),
            "change_percent": str(self.change_percent),
            "volume": str(self.volume),
            "exchange": self.exchange.value,
            "is_market_open": self.is_market_open,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class FinancialHighlights:
    """Financial statement highlights (Income Statement, Balance Sheet, Cash Flow)."""

    company_name: str
    total_revenue: Decimal
    net_income: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    operating_cash_flow: Decimal
    free_cash_flow: Decimal

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_name": self.company_name,
            "total_revenue": str(self.total_revenue),
            "net_income": str(self.net_income),
            "total_assets": str(self.total_assets),
            "total_liabilities": str(self.total_liabilities),
            "operating_cash_flow": str(self.operating_cash_flow),
            "free_cash_flow": str(self.free_cash_flow),
        }


@dataclass(frozen=True)
class TechnicalAnalysisSection:
    """Technical price action & OHLCV bar analysis section."""

    timeframe: Timeframe
    candle_count: int
    trend_summary: str
    last_close: Price

    def to_dict(self) -> dict[str, Any]:
        return {
            "timeframe": self.timeframe.value,
            "candle_count": self.candle_count,
            "trend_summary": self.trend_summary,
            "last_close": str(self.last_close.amount),
        }


@dataclass(frozen=True)
class NewsSection:
    """Market news headlines & sentiment summary."""

    article_count: int
    avg_sentiment_score: float
    headlines: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "article_count": self.article_count,
            "avg_sentiment_score": self.avg_sentiment_score,
            "headlines": list(self.headlines),
            "sources": list(self.sources),
        }


@dataclass(frozen=True)
class CorporateActionsSection:
    """Corporate action events summary."""

    actions_count: int
    actions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "actions_count": self.actions_count,
            "actions": list(self.actions),
        }


@dataclass(frozen=True)
class MacroContextSection:
    """Macroeconomic indicator & calendar context."""

    series_name: str
    repo_rate: str
    upcoming_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "series_name": self.series_name,
            "repo_rate": self.repo_rate,
            "upcoming_events": list(self.upcoming_events),
        }


@dataclass(frozen=True)
class AgentOpinionModel:
    """Individual AI specialist agent opinion payload."""

    agent_type: str
    recommendation: str
    score: float
    confidence: float
    reasoning: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_type": self.agent_type,
            "recommendation": self.recommendation,
            "score": self.score,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
        }


@dataclass(frozen=True)
class AgentOpinionsSection:
    """Multi-agent committee opinions summary."""

    opinions: list[AgentOpinionModel] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"opinions": [op.to_dict() for op in self.opinions]}


@dataclass(frozen=True)
class ConsensusDecisionSection:
    """Consensus Engine decision summary."""

    winning_recommendation: RecommendationType
    consensus_score: float
    composite_confidence: float
    agreement_ratio: float
    conflict_count: int
    session_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "winning_recommendation": self.winning_recommendation.value,
            "consensus_score": self.consensus_score,
            "composite_confidence": self.composite_confidence,
            "agreement_ratio": self.agreement_ratio,
            "conflict_count": self.conflict_count,
            "session_id": self.session_id,
        }


@dataclass(frozen=True)
class ExplainabilitySection:
    """Detailed explainability, evidence, conflicts, and reasoning breakdown."""

    evidence: list[SupportingEvidence]
    reasoning: str
    agent_contributions: dict[str, float]
    confidence: float
    conflicts: list[str]
    assumptions: list[str]
    unknowns: list[str]
    key_risks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence": [ev.to_dict() for ev in self.evidence],
            "reasoning": self.reasoning,
            "agent_contributions": dict(self.agent_contributions),
            "confidence": self.confidence,
            "conflicts": list(self.conflicts),
            "assumptions": list(self.assumptions),
            "unknowns": list(self.unknowns),
            "key_risks": list(self.key_risks),
        }


@dataclass(frozen=True)
class ExecutiveSummary:
    """High-level executive investment summary."""

    investment_thesis: str
    key_strengths: list[str]
    primary_risks: list[str]
    target_horizon: str
    final_recommendation: RecommendationType

    def to_dict(self) -> dict[str, Any]:
        return {
            "investment_thesis": self.investment_thesis,
            "key_strengths": list(self.key_strengths),
            "primary_risks": list(self.primary_risks),
            "target_horizon": self.target_horizon,
            "final_recommendation": self.final_recommendation.value,
        }


@dataclass(frozen=True)
class ResearchReport:
    """
    Final Institutional Investment Research Report Aggregate.
    """

    ticker: str
    company_name: str
    session_id: str
    timestamp: Timestamp
    executive_summary: ExecutiveSummary
    market_snapshot: MarketSnapshot
    financial_highlights: FinancialHighlights
    technical_analysis: TechnicalAnalysisSection
    news_section: NewsSection
    corporate_actions: CorporateActionsSection
    macro_context: MacroContextSection
    agent_opinions: AgentOpinionsSection
    consensus_decision: ConsensusDecisionSection
    explainability: ExplainabilitySection
    bull_case: list[str]
    bear_case: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize complete report to structured dictionary."""
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "executive_summary": self.executive_summary.to_dict(),
            "market_snapshot": self.market_snapshot.to_dict(),
            "financial_highlights": self.financial_highlights.to_dict(),
            "technical_analysis": self.technical_analysis.to_dict(),
            "news_section": self.news_section.to_dict(),
            "corporate_actions": self.corporate_actions.to_dict(),
            "macro_context": self.macro_context.to_dict(),
            "agent_opinions": self.agent_opinions.to_dict(),
            "consensus_decision": self.consensus_decision.to_dict(),
            "explainability": self.explainability.to_dict(),
            "bull_case": list(self.bull_case),
            "bear_case": list(self.bear_case),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize report to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Render report as formatted GitHub-Flavored Markdown."""
        lines = [
            f"# Investment Research Report: {self.company_name} ({self.ticker})",
            f"**Session ID**: `{self.session_id}` | **Date**: {self.timestamp.isoformat()}",
            "",
            "## 1. Executive Summary",
            f"- **Final Recommendation**: **{self.executive_summary.final_recommendation.value}**",
            f"- **Target Horizon**: {self.executive_summary.target_horizon}",
            f"- **Investment Thesis**: {self.executive_summary.investment_thesis}",
            "",
            "### Key Strengths",
            "\n".join(f"- {s}" for s in self.executive_summary.key_strengths),
            "",
            "### Primary Risks",
            "\n".join(f"- {r}" for r in self.executive_summary.primary_risks),
            "",
            "## 2. Market Snapshot",
            f"- **Current Price**: {self.market_snapshot.price.amount} {self.market_snapshot.price.money.currency}",
            f"- **Change**: {self.market_snapshot.change_percent}%",
            f"- **Volume**: {self.market_snapshot.volume}",
            f"- **Exchange**: {self.market_snapshot.exchange.value}",
            f"- **Session Open**: {self.market_snapshot.is_market_open}",
            "",
            "## 3. Financial Highlights",
            f"- **Total Revenue**: {self.financial_highlights.total_revenue}",
            f"- **Net Income**: {self.financial_highlights.net_income}",
            f"- **Total Assets**: {self.financial_highlights.total_assets}",
            f"- **Total Liabilities**: {self.financial_highlights.total_liabilities}",
            f"- **Operating Cash Flow**: {self.financial_highlights.operating_cash_flow}",
            f"- **Free Cash Flow**: {self.financial_highlights.free_cash_flow}",
            "",
            "## 4. Technical Analysis",
            f"- **Timeframe**: {self.technical_analysis.timeframe.value}",
            f"- **Bar Count**: {self.technical_analysis.candle_count}",
            f"- **Trend Summary**: {self.technical_analysis.trend_summary}",
            f"- **Last Close**: {self.technical_analysis.last_close.amount}",
            "",
            "## 5. Recent News & Sentiment",
            f"- **Articles Analyzed**: {self.news_section.article_count}",
            f"- **Avg Sentiment Score**: {self.news_section.avg_sentiment_score}",
            "### Headlines",
            "\n".join(f"- {h}" for h in self.news_section.headlines),
            "",
            "## 6. Corporate Actions",
            f"- **Actions Count**: {self.corporate_actions.actions_count}",
            "\n".join(
                f"- {act.get('action_type', 'EVENT')}: {act.get('description', 'Corporate action')}"
                for act in self.corporate_actions.actions
            ),
            "",
            "## 7. Macroeconomic Context",
            f"- **Indicator**: {self.macro_context.series_name}",
            f"- **Repo Rate**: {self.macro_context.repo_rate}",
            "",
            "## 8. Multi-Agent Committee Opinions",
            "\n".join(
                f"### Agent: {op.agent_type}\n"
                f"- **Recommendation**: {op.recommendation}\n"
                f"- **Score**: {op.score} | **Confidence**: {op.confidence}\n"
                f"- **Reasoning**: {op.reasoning}\n"
                for op in self.agent_opinions.opinions
            ),
            "",
            "## 9. Consensus Decision",
            f"- **Committee Recommendation**: **{self.consensus_decision.winning_recommendation.value}**",
            f"- **Consensus Score**: {self.consensus_decision.consensus_score}",
            f"- **Composite Confidence**: {self.consensus_decision.composite_confidence}",
            f"- **Agreement Ratio**: {round(self.consensus_decision.agreement_ratio * 100, 1)}%",
            f"- **Conflicts Identified**: {self.consensus_decision.conflict_count}",
            "",
            "## 10. Explainability & Evidence Attribution",
            f"**Reasoning Trace**: {self.explainability.reasoning}",
            "",
            "### Supporting Evidence & Source Citations",
        ]

        for ev in self.explainability.evidence:
            lines.append(f"- **Fact**: {ev.fact} (Confidence: {ev.confidence_score})")
            for c in ev.citations:
                lines.append(
                    f'  - *Source*: [{c.filing_type} - {c.company} (Page {c.page}) - Doc `{c.document_id}`] Snippet: "{c.snippet}"'
                )

        lines.extend(
            [
                "",
                "### Bull Case",
                "\n".join(f"- {b}" for b in self.bull_case),
                "",
                "### Bear Case",
                "\n".join(f"- {b}" for b in self.bear_case),
                "",
                "### Assumptions & Unknowns",
                "**Assumptions**:",
                "\n".join(f"- {a}" for a in self.explainability.assumptions),
                "**Unknowns**:",
                "\n".join(f"- {u}" for u in self.explainability.unknowns),
            ]
        )

        return "\n".join(lines)

    def to_pdf_metadata(self) -> dict[str, Any]:
        """Prepare architecture metadata for future PDF document generation."""
        return {
            "document_title": f"Investment Research Report - {self.ticker}",
            "author": "MONEYYYYYY AI Investment Operating System",
            "subject": f"Company Intelligence Report for {self.company_name}",
            "keywords": ["Equity Research", self.ticker, "Multi-Agent Consensus", "SEBI"],
            "created_at": self.timestamp.isoformat(),
            "sections_count": 10,
            "session_id": self.session_id,
        }
