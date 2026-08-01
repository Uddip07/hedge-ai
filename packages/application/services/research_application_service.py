"""
ResearchApplicationService Implementation.

Coordinates research workflows, orchestration services, and stock analysis use cases.
"""

import uuid

from packages.application.commands.analyze_stock_command import AnalyzeStockCommand
from packages.application.dto.analyze_stock_dto import AnalyzeStockResultDTO
from packages.application.services.base import BaseApplicationService
from packages.application.use_cases.analyze_stock_use_case import AnalyzeStockUseCase


class ResearchApplicationService(BaseApplicationService):
    """
    Application Service coordinating investment research workflows and use cases.

    Attributes:
        analyze_stock_use_case (AnalyzeStockUseCase): Injected single-stock analysis use case.
    """

    def __init__(self, analyze_stock_use_case: AnalyzeStockUseCase) -> None:
        self.analyze_stock_use_case = analyze_stock_use_case

    def analyze_stock(
        self,
        ticker_symbol: str,
        portfolio_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        investment_horizon_days: int = 365,
    ) -> AnalyzeStockResultDTO:
        """
        Orchestrate single-stock investment analysis workflow.

        Args:
            ticker_symbol (str): Ticker symbol string (e.g. "RELIANCE.NSE").
            portfolio_id (uuid.UUID | None): Target portfolio ID for suitability checks.
            user_id (uuid.UUID | None): Actor/User initiating the research request.
            investment_horizon_days (int): Target investment holding period in days.

        Returns:
            AnalyzeStockResultDTO: Complete stock analysis result payload.
        """
        cmd = AnalyzeStockCommand(
            user_id=user_id,
            ticker_symbol=ticker_symbol,
            portfolio_id=portfolio_id,
            investment_horizon_days=investment_horizon_days,
        )
        return self.analyze_stock_use_case.execute(cmd)
