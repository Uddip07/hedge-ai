"""
AnalyzeStockUseCase Implementation.

Orchestrates single-stock investment research, ticker validation, market data retrieval,
research score retrieval, risk evaluation, and portfolio suitability verification.
"""

from decimal import Decimal

from packages.application.commands.analyze_stock_command import AnalyzeStockCommand
from packages.application.dto.analyze_stock_dto import AnalyzeStockResultDTO
from packages.application.exceptions import ValidationApplicationError
from packages.application.mappers.stock_analysis_mapper import StockAnalysisMapper
from packages.application.ports.market_data_port import MarketDataPort
from packages.application.ports.portfolio_port import PortfolioPort
from packages.application.ports.research_port import ResearchPort
from packages.application.use_cases.base import BaseUseCase
from packages.domain.enums.research import RecommendationType
from packages.domain.enums.risk import RiskLevel
from packages.domain.exceptions import ValidationError
from packages.domain.policies.portfolio_policy import PortfolioPolicy
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId
from packages.domain.value_objects.metrics.scores import RecommendationScore
from packages.domain.value_objects.temporal.timestamps import Timestamp


class AnalyzeStockUseCase(BaseUseCase[AnalyzeStockCommand, AnalyzeStockResultDTO]):
    """
    Application Use Case orchestrating end-to-end single-stock investment analysis.

    Dependencies:
        research_port (ResearchPort): Outbound port for research reports & consensus scores.
        portfolio_port (PortfolioPort): Outbound port for portfolio data querying.
        market_data_port (MarketDataPort | None): Outbound port for market price & company data.
    """

    def __init__(
        self,
        research_port: ResearchPort,
        portfolio_port: PortfolioPort,
        market_data_port: MarketDataPort | None = None,
        mapper: StockAnalysisMapper | None = None,
    ) -> None:
        self.research_port = research_port
        self.portfolio_port = portfolio_port
        self.market_data_port = market_data_port
        self.mapper = mapper or StockAnalysisMapper()
        self.portfolio_policy = PortfolioPolicy()

    def execute(self, request: AnalyzeStockCommand) -> AnalyzeStockResultDTO:
        """
        Execute the stock analysis workflow.

        Steps:
            1. Ticker Validation
            2. Market Data Retrieval (Price & Profile)
            3. Research Request (Consensus Score & Recommendation)
            4. Risk Evaluation (RiskLevel determination)
            5. Portfolio Suitability Verification
            6. Map & Return DTO

        Raises:
            ValidationApplicationError: If ticker validation fails.
        """
        # Step 1: Ticker validation
        try:
            ticker = Ticker(request.ticker_symbol)
        except ValidationError as exc:
            raise ValidationApplicationError(
                f"Invalid ticker symbol format: '{request.ticker_symbol}'.",
                context={"ticker_symbol": request.ticker_symbol},
            ) from exc

        # Step 2: Market Data Retrieval
        market_data_info = ""
        if self.market_data_port is not None:
            latest_price = self.market_data_port.get_latest_price(ticker)
            company_profile = self.market_data_port.get_company_profile(ticker)
            company_name = company_profile.name if company_profile else ticker.symbol
            market_data_info = f" Market price: {latest_price.amount} {latest_price.money.currency.code} for {company_name}."

        # Step 3: Research request
        score = self.research_port.get_latest_recommendation_score(ticker)
        if score is None:
            # No research score available — use a neutral baseline (HOLD at 0.50).
            # This avoids fabricating a bullish signal when no evidence exists.
            # The AI committee will generate a real score on the next research cycle.
            score = RecommendationScore(Decimal("0.50"))
            recommendation = RecommendationType.HOLD
            reasoning = f"No research score available for {ticker.full_symbol}. Neutral baseline applied pending AI committee evaluation.{market_data_info}"
        else:
            if score.value >= Decimal("0.80"):
                recommendation = RecommendationType.STRONG_BUY
            elif score.value >= Decimal("0.60"):
                recommendation = RecommendationType.BUY
            elif score.value >= Decimal("0.40"):
                recommendation = RecommendationType.HOLD
            else:
                recommendation = RecommendationType.SELL
            reasoning = f"Multi-agent committee consensus score evaluated at {score.value} for {ticker.full_symbol}.{market_data_info}"

        # Step 4: Risk evaluation
        if score.value >= Decimal("0.70"):
            risk_level = RiskLevel.LOW
        elif score.value >= Decimal("0.40"):
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH

        # Step 5: Portfolio suitability verification
        is_suitable = True
        if request.portfolio_id is not None:
            p_id = PortfolioId(request.portfolio_id)
            portfolio = self.portfolio_port.get_portfolio_by_id(p_id)
            if portfolio is not None:
                is_valid, violations = self.portfolio_policy.validate_portfolio_limits(portfolio)
                if not is_valid:
                    is_suitable = False
                    reasoning += f" Portfolio policy violations: {'; '.join(violations)}"

        # Step 6: Map to DTO and return
        domain_context = {
            "ticker": ticker,
            "recommendation": recommendation,
            "consensus_score": score,
            "risk_level": risk_level,
            "is_suitable": is_suitable,
            "reasoning_summary": reasoning,
            "timestamp": Timestamp.now_utc(),
        }

        return self.mapper.to_dto(domain_context)
