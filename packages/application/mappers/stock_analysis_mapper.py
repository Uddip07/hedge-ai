"""
StockAnalysisMapper for Application Layer.

Maps domain objects (Ticker, RecommendationType, ConsensusDecision, RiskLevel, Timestamp)
to AnalyzeStockResultDTO structures.
"""

from decimal import Decimal
from typing import Any

from packages.application.dto.analyze_stock_dto import AnalyzeStockResultDTO
from packages.application.mappers.base import BaseMapper
from packages.domain.enums.research import RecommendationType
from packages.domain.enums.risk import RiskLevel
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.metrics.scores import RecommendationScore
from packages.domain.value_objects.temporal.timestamps import Timestamp


class StockAnalysisMapper(BaseMapper[dict[str, Any], AnalyzeStockResultDTO]):
    """
    Mapper transforming domain stock analysis assessment components into AnalyzeStockResultDTO.
    """

    def to_dto(self, domain: dict[str, Any]) -> AnalyzeStockResultDTO:
        """
        Map domain evaluation context dictionary to AnalyzeStockResultDTO.

        Expected domain dict keys:
            - ticker (Ticker): Asset ticker value object.
            - recommendation (RecommendationType): Directional recommendation.
            - consensus_score (RecommendationScore): Multi-agent consensus score.
            - risk_level (RiskLevel): Evaluated risk level.
            - is_suitable (bool): Portfolio suitability flag.
            - reasoning_summary (str): Analytical rationale summary text.
            - timestamp (Timestamp): Valuation timestamp.
        """
        ticker: Ticker = domain["ticker"]
        rec: RecommendationType = domain["recommendation"]
        score: RecommendationScore = domain["consensus_score"]
        risk: RiskLevel = domain["risk_level"]
        is_suitable: bool = bool(domain.get("is_suitable", True))
        summary: str = domain.get("reasoning_summary", "Analysis completed successfully.")
        ts: Timestamp = domain.get("timestamp", Timestamp.now_utc())

        return AnalyzeStockResultDTO(
            ticker=ticker.full_symbol,
            recommendation=rec.value,
            consensus_score=float(score.value),
            risk_level=risk.value,
            is_suitable_for_portfolio=is_suitable,
            reasoning_summary=summary,
            analyzed_at=ts.isoformat(),
        )

    def to_domain(self, dto: AnalyzeStockResultDTO) -> dict[str, Any]:
        """Map AnalyzeStockResultDTO back to domain context components."""
        return {
            "ticker": Ticker(dto.ticker),
            "recommendation": RecommendationType(dto.recommendation),
            "consensus_score": RecommendationScore(Decimal(str(dto.consensus_score))),
            "risk_level": RiskLevel(dto.risk_level),
            "is_suitable": dto.is_suitable_for_portfolio,
            "reasoning_summary": dto.reasoning_summary,
            "timestamp": Timestamp.from_isoformat(dto.analyzed_at),
        }
