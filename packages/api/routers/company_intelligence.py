"""
Company Intelligence Router.

Provides GET /company-intelligence/{ticker} endpoint for orchestrating end-to-end company research reports.
"""

from fastapi import APIRouter, Depends, status

from packages.api.dependencies import get_company_intelligence_orchestrator
from packages.api.schemas.response import CompanyIntelligenceResponse
from packages.application.company_intelligence import CompanyIntelligenceOrchestrator

router = APIRouter(prefix="/company-intelligence", tags=["Company Intelligence"])


@router.get(
    "/{ticker}",
    response_model=CompanyIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get End-to-End Company Research Report",
    description="Orchestrates financial statement analysis, market data snapshot, RAG filing discovery, news sentiment, and multi-agent committee consensus into a structured report.",
)
async def get_company_intelligence(
    ticker: str,
    orchestrator: CompanyIntelligenceOrchestrator = Depends(get_company_intelligence_orchestrator),
) -> CompanyIntelligenceResponse:
    """
    Execute end-to-end Company Intelligence research workflow.

    Args:
        ticker (str): Asset ticker symbol string (e.g. 'RELIANCE', 'INFY.NSE').
        orchestrator (CompanyIntelligenceOrchestrator): Injected orchestrator.

    Returns:
        CompanyIntelligenceResponse: Structured research report DTO payload.
    """
    report = orchestrator.analyze_company(ticker_symbol=ticker)
    d = report.to_dict()

    return CompanyIntelligenceResponse(
        ticker=d["ticker"],
        company_name=d["company_name"],
        session_id=d["session_id"],
        timestamp=d["timestamp"],
        executive_summary=d["executive_summary"],
        market_snapshot=d["market_snapshot"],
        financial_highlights=d["financial_highlights"],
        technical_analysis=d["technical_analysis"],
        news_section=d["news_section"],
        corporate_actions=d["corporate_actions"],
        macro_context=d["macro_context"],
        agent_opinions=d["agent_opinions"],
        consensus_decision=d["consensus_decision"],
        explainability=d["explainability"],
        bull_case=d["bull_case"],
        bear_case=d["bear_case"],
    )
