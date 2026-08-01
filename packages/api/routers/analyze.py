"""
Investment Analysis Router.

Provides POST /analyze endpoint for orchestrating single-stock investment research.
"""

from fastapi import APIRouter, Depends, status

from packages.api.dependencies import get_analyze_stock_use_case
from packages.api.schemas.request import AnalyzeStockRequest
from packages.api.schemas.response import AnalyzeStockResponse
from packages.application.commands import AnalyzeStockCommand
from packages.application.use_cases import AnalyzeStockUseCase

router = APIRouter(prefix="", tags=["Investment Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeStockResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Single Stock",
    description="Orchestrate end-to-end single-stock investment research, risk evaluation, and portfolio suitability.",
)
async def analyze_stock(
    body: AnalyzeStockRequest,
    use_case: AnalyzeStockUseCase = Depends(get_analyze_stock_use_case),
) -> AnalyzeStockResponse:
    """
    Trigger single-stock investment research workflow.

    Args:
        body (AnalyzeStockRequest): Validated request payload containing ticker and options.
        use_case (AnalyzeStockUseCase): Injected application use case.

    Returns:
        AnalyzeStockResponse: Analysis results DTO payload.
    """
    command = AnalyzeStockCommand(
        ticker_symbol=body.ticker,
        portfolio_id=body.portfolio_id,
        investment_horizon_days=body.investment_horizon_days,
    )
    result = use_case.execute(command)

    return AnalyzeStockResponse(
        ticker=result.ticker,
        recommendation=result.recommendation,
        consensus_score=result.consensus_score,
        risk_level=result.risk_level,
        is_suitable_for_portfolio=result.is_suitable_for_portfolio,
        reasoning_summary=result.reasoning_summary,
        analyzed_at=result.analyzed_at,
    )
