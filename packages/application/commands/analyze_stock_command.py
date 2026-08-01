"""
AnalyzeStockCommand for CQRS Architecture.

Write command carrying request payload for orchestrating single-stock investment analysis.
"""

import uuid
from dataclasses import dataclass
from typing import Any

from packages.application.commands.base import BaseCommand
from packages.application.exceptions import ValidationApplicationError


@dataclass(frozen=True, kw_only=True)
class AnalyzeStockCommand(BaseCommand):
    """
    Command carrying input parameters to trigger single-stock analysis.

    Attributes:
        ticker_symbol (str): Asset ticker symbol (e.g. "RELIANCE.NSE", "TCS.BSE").
        portfolio_id (uuid.UUID | None): Optional portfolio ID for suitability checks.
        investment_horizon_days (int): Target investment holding period in days.
    """

    ticker_symbol: str
    portfolio_id: uuid.UUID | None = None
    investment_horizon_days: int = 365

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.ticker_symbol or not self.ticker_symbol.strip():
            raise ValidationApplicationError("Ticker symbol cannot be empty.")
        if self.portfolio_id is not None and not isinstance(self.portfolio_id, uuid.UUID):
            object.__setattr__(self, "portfolio_id", uuid.UUID(str(self.portfolio_id)))
        if self.investment_horizon_days <= 0:
            raise ValidationApplicationError("Investment horizon days must be strictly positive.")

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "ticker_symbol": self.ticker_symbol,
                "portfolio_id": str(self.portfolio_id) if self.portfolio_id else None,
                "investment_horizon_days": self.investment_horizon_days,
            }
        )
        return d
