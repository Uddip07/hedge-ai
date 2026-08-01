"""
Research Report Builder for Company Intelligence Engine.

Constructs structured institutional ResearchReport instances from workflow execution outputs,
populating Executive Summaries, Financial Highlights, Technical Analysis, News, Corporate Actions,
Macro Context, Agent Opinions, Consensus Decisions, and Explainability sections.
"""

from typing import Any

from packages.ai.consensus.models import ConsensusIntelligenceDecision
from packages.ai.models.agent_result import AgentResult
from packages.application.company_intelligence.exceptions import ReportGenerationError
from packages.application.company_intelligence.models import (
    AgentOpinionModel,
    AgentOpinionsSection,
    CompanyIntelligenceContext,
    ConsensusDecisionSection,
    CorporateActionsSection,
    ExecutiveSummary,
    ExplainabilitySection,
    FinancialHighlights,
    MacroContextSection,
    MarketSnapshot,
    NewsSection,
    ResearchReport,
    SupportingEvidence,
    TechnicalAnalysisSection,
)
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


class ResearchReportBuilder:
    """
    Builder constructing complete ResearchReport aggregates.
    """

    def build_report(self, workflow_payload: dict[str, Any]) -> ResearchReport:
        """
        Build ResearchReport from workflow output dictionary.

        Args:
            workflow_payload (dict[str, Any]): Compiled pipeline stage outputs.

        Returns:
            ResearchReport: Structured research report domain aggregate.
        """
        try:
            context: CompanyIntelligenceContext = workflow_payload["context"]
            ticker: Ticker = workflow_payload["ticker"]
            market_snapshot: MarketSnapshot = workflow_payload["market_snapshot"]
            financial_highlights: FinancialHighlights = workflow_payload["financial_highlights"]
            technical_analysis: TechnicalAnalysisSection = workflow_payload["technical_analysis"]
            news_section: NewsSection = workflow_payload["news_section"]
            corporate_actions: CorporateActionsSection = workflow_payload["corporate_actions"]
            macro_context: MacroContextSection = workflow_payload["macro_context"]
            rag_evidence: list[SupportingEvidence] = workflow_payload["rag_evidence"]
            agent_results: list[AgentResult] = workflow_payload["agent_results"]
            consensus_decision: ConsensusIntelligenceDecision = workflow_payload[
                "consensus_decision"
            ]

            # Build AgentOpinionsSection
            opinion_models = [
                AgentOpinionModel(
                    agent_type=res.agent_type.value,
                    recommendation=res.recommendation.value,
                    score=float(res.score.value),
                    confidence=float(res.confidence.value),
                    reasoning=res.reasoning,
                )
                for res in agent_results
            ]
            agent_opinions = AgentOpinionsSection(opinions=opinion_models)

            # Build ConsensusDecisionSection
            consensus_section = ConsensusDecisionSection(
                winning_recommendation=consensus_decision.recommendation,
                consensus_score=float(consensus_decision.score.value),
                composite_confidence=float(consensus_decision.confidence.value),
                agreement_ratio=consensus_decision.agreement_score,
                conflict_count=len(consensus_decision.conflicts),
                session_id=context.session_id,
            )

            # Build ExplainabilitySection
            agent_contribs = {
                res.agent_type.value: float(res.confidence.value) for res in agent_results
            }
            conflicts_list = [c.description for c in consensus_decision.conflicts]
            all_risks = [r for res in agent_results for r in res.risks] or [
                "Raw material input cost inflation",
                "Regulatory policy changes",
            ]
            all_assumptions = [a for res in agent_results for a in res.assumptions] or [
                "Consistent quarterly revenue growth",
                "Stable domestic market demand",
            ]
            all_unknowns = [u for res in agent_results for u in res.unknowns] or [
                "Unscheduled executive leadership revisions"
            ]

            drivers_summary = (
                "; ".join(consensus_decision.explanation.key_drivers)
                if consensus_decision.explanation.key_drivers
                else "Multi-agent fundamental and technical convergence."
            )
            explainability = ExplainabilitySection(
                evidence=rag_evidence,
                reasoning=f"{drivers_summary} (Status: {consensus_decision.explanation.policy_compliance_status})",
                agent_contributions=agent_contribs,
                confidence=float(consensus_decision.confidence.value),
                conflicts=conflicts_list,
                assumptions=all_assumptions,
                unknowns=all_unknowns,
                key_risks=all_risks,
            )

            # Build Executive Summary
            exec_summary = ExecutiveSummary(
                investment_thesis=(
                    f"Institutional multi-agent committee consensus evaluates {financial_highlights.company_name} "
                    f"({ticker.full_symbol}) with a {consensus_decision.recommendation.value} thesis based on "
                    f"strong financial balance sheet metrics, revenue growth, and positive technical momentum."
                ),
                key_strengths=[
                    f"Revenue: INR {financial_highlights.total_revenue}",
                    f"Operating Cash Flow: INR {financial_highlights.operating_cash_flow}",
                    f"Technical trend: {technical_analysis.trend_summary}",
                ],
                primary_risks=all_risks[:3],
                target_horizon="12 Months",
                final_recommendation=consensus_decision.recommendation,
            )

            bull_case = [
                f"Revenue expansion exceeds industry average at INR {financial_highlights.total_revenue}.",
                f"Free cash flow generation remains healthy at INR {financial_highlights.free_cash_flow}.",
                "News sentiment indicates positive institutional investor sentiment.",
            ]
            bear_case = [
                f"Macroeconomic sensitivity to repo rate changes ({macro_context.repo_rate}).",
                f"Potential input cost inflation: {all_risks[0] if all_risks else 'Input inflation'}.",
            ]

            return ResearchReport(
                ticker=ticker.full_symbol,
                company_name=financial_highlights.company_name,
                session_id=context.session_id,
                timestamp=Timestamp.now_utc(),
                executive_summary=exec_summary,
                market_snapshot=market_snapshot,
                financial_highlights=financial_highlights,
                technical_analysis=technical_analysis,
                news_section=news_section,
                corporate_actions=corporate_actions,
                macro_context=macro_context,
                agent_opinions=agent_opinions,
                consensus_decision=consensus_section,
                explainability=explainability,
                bull_case=bull_case,
                bear_case=bear_case,
            )
        except Exception as err:
            raise ReportGenerationError(
                f"Failed to build research report: {err}",
            ) from err
