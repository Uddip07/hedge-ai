"""
AnalyzeStockResultDTO Data Transfer Object.

Carries output analysis payload returned by AnalyzeStockUseCase.
"""

from dataclasses import dataclass
from typing import Any

from packages.application.dto.base import BaseDTO


@dataclass(frozen=True)
class AnalyzeStockResultDTO(BaseDTO):
    """
    Data Transfer Object carrying single-stock investment analysis results.

    Attributes:
        ticker (str): Asset ticker symbol (e.g. "RELIANCE.NSE").
        recommendation (str): Directional recommendation (e.g. "BUY", "HOLD", "SELL").
        consensus_score (float): Normalized multi-agent consensus score [0.0, 1.0].
        risk_level (str): Calculated risk evaluation level ("LOW", "MEDIUM", "HIGH", "CRITICAL").
        is_suitable_for_portfolio (bool): Suitability status against target portfolio policies.
        reasoning_summary (str): Executive summary of analytical reasoning.
        analyzed_at (str): ISO-8601 timestamp of analysis completion.
    """

    ticker: str
    recommendation: str
    consensus_score: float
    risk_level: str
    is_suitable_for_portfolio: bool
    reasoning_summary: str
    analyzed_at: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize DTO to dictionary format."""
        return {
            "ticker": self.ticker,
            "recommendation": self.recommendation,
            "consensus_score": self.consensus_score,
            "risk_level": self.risk_level,
            "is_suitable_for_portfolio": self.is_suitable_for_portfolio,
            "reasoning_summary": self.reasoning_summary,
            "analyzed_at": self.analyzed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalyzeStockResultDTO":
        """Deserialize dictionary format to DTO instance."""
        return cls(
            ticker=data["ticker"],
            recommendation=data["recommendation"],
            consensus_score=float(data["consensus_score"]),
            risk_level=data["risk_level"],
            is_suitable_for_portfolio=bool(data["is_suitable_for_portfolio"]),
            reasoning_summary=data["reasoning_summary"],
            analyzed_at=data["analyzed_at"],
        )
