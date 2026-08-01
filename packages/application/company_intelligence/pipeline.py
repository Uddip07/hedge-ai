"""
Company Intelligence Pipeline Implementation.

Executes sequential pipeline stages from Ticker Normalization through Market Data,
RAG Retrieval, Multi-Agent Evaluation, and Consensus Calculations.
"""

from typing import Any

from packages.ai.models.agent_context import AgentContext
from packages.application.company_intelligence.exceptions import PipelineExecutionError
from packages.application.company_intelligence.models import (
    CompanyIntelligenceContext,
    CorporateActionsSection,
    FinancialHighlights,
    MacroContextSection,
    MarketSnapshot,
    NewsSection,
    SupportingEvidence,
    TechnicalAnalysisSection,
)
from packages.application.company_intelligence.services import (
    CompanyAgentCoordinatorService,
    CompanyDataRetrievalService,
    CompanyDocumentService,
)
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.normalizers.ticker import TickerNormalizer


class CompanyIntelligencePipeline:
    """
    Sequential execution pipeline for Company Intelligence Workflow.
    """

    def __init__(
        self,
        data_retrieval_service: CompanyDataRetrievalService,
        document_service: CompanyDocumentService,
        agent_coordinator_service: CompanyAgentCoordinatorService,
    ) -> None:
        self.data_retrieval_service = data_retrieval_service
        self.document_service = document_service
        self.agent_coordinator_service = agent_coordinator_service

    def execute_pipeline(
        self, raw_ticker_symbol: str, session_id: str | None = None
    ) -> dict[str, Any]:
        """
        Execute full end-to-end company intelligence pipeline.

        Returns:
            dict[str, Any]: Dictionary payload containing all intermediate stage outputs.
        """
        try:
            # 1. Ticker Normalization
            normalized_symbol = TickerNormalizer.from_provider_symbol(raw_ticker_symbol)
            ticker = Ticker(normalized_symbol.full_symbol)

            context = CompanyIntelligenceContext(
                ticker=ticker,
                session_id=session_id or "",
            )

            # 2. Market Snapshot Retrieval
            market_snapshot: MarketSnapshot = self.data_retrieval_service.retrieve_market_snapshot(
                ticker
            )

            # 3. Financial Highlights Retrieval
            financial_highlights: FinancialHighlights = (
                self.data_retrieval_service.retrieve_financial_highlights(ticker)
            )

            # 4. Technical Analysis Retrieval
            technical_analysis: TechnicalAnalysisSection = (
                self.data_retrieval_service.retrieve_technical_analysis(ticker)
            )

            # 5. News Retrieval
            news_section: NewsSection = self.data_retrieval_service.retrieve_news_section(ticker)

            # 6. Corporate Actions Retrieval
            corporate_actions: CorporateActionsSection = (
                self.data_retrieval_service.retrieve_corporate_actions(ticker)
            )

            # 7. Macro Context Retrieval
            macro_context: MacroContextSection = self.data_retrieval_service.retrieve_macro_context(
                "IN"
            )

            # 8. Document Discovery & RAG Retrieval
            rag_evidence: list[SupportingEvidence] = (
                self.document_service.discover_and_retrieve_rag_evidence(ticker)
            )

            # 9. Multi-Agent Committee Evaluation & Consensus Engine
            agent_ctx = AgentContext(
                ticker=ticker,
                session_id=context.session_id,
            )
            agent_results, consensus_decision = self.agent_coordinator_service.evaluate_committee(
                agent_ctx
            )

            return {
                "context": context,
                "ticker": ticker,
                "market_snapshot": market_snapshot,
                "financial_highlights": financial_highlights,
                "technical_analysis": technical_analysis,
                "news_section": news_section,
                "corporate_actions": corporate_actions,
                "macro_context": macro_context,
                "rag_evidence": rag_evidence,
                "agent_results": agent_results,
                "consensus_decision": consensus_decision,
            }
        except Exception as err:
            raise PipelineExecutionError(
                f"Company Intelligence Pipeline failed for '{raw_ticker_symbol}': {err}",
                details={"raw_ticker": raw_ticker_symbol},
            ) from err
