"""
Request Schemas for MONEYYYYYY API endpoints using Pydantic v2.
"""

import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalyzeStockRequest(BaseModel):
    """
    Request payload model for POST /analyze endpoint.

    Attributes:
        ticker (str): Asset ticker symbol (e.g. "RELIANCE", "RELIANCE.NSE", "TCS.BSE").
        portfolio_id (uuid.UUID | None): Optional portfolio ID for suitability checks.
        investment_horizon_days (int): Target investment horizon in days (default 365).
    """

    ticker: str = Field(
        ...,
        description="Asset ticker symbol (e.g. 'RELIANCE', 'TCS.NSE').",
        examples=["RELIANCE", "TCS.NSE"],
    )
    portfolio_id: uuid.UUID | None = Field(
        default=None,
        description="Optional portfolio UUID for suitability verification.",
    )
    investment_horizon_days: int = Field(
        default=365,
        ge=1,
        le=3650,
        description="Target investment holding period in days.",
    )

    @field_validator("ticker")
    @classmethod
    def validate_and_normalize_ticker(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ticker symbol cannot be empty.")
        clean_v = v.strip().upper()
        if "." not in clean_v:
            clean_v = f"{clean_v}.NSE"
        return clean_v


class EvaluateCommitteeRequest(BaseModel):
    """
    Request payload model for POST /committee/evaluate endpoint.
    """

    ticker: str = Field(
        ...,
        description="Target asset ticker symbol (e.g. 'RELIANCE', 'INFY.NSE').",
        examples=["RELIANCE", "INFY.NSE"],
    )
    horizon: Literal["INTRADAY", "DAILY", "SWING", "LONG_TERM"] = Field(
        default="LONG_TERM",
        description="Target investment holding period horizon.",
    )
    style: Literal["VALUE", "GROWTH", "QUANTITATIVE", "TECHNICAL", "BALANCED"] = Field(
        default="BALANCED",
        description="Investment management style classification.",
    )
    user_query: str = Field(
        default="Execute comprehensive investment analysis.",
        description="User research request instructions.",
    )

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ticker symbol cannot be empty.")
        clean_v = v.strip().upper()
        if "." not in clean_v:
            clean_v = f"{clean_v}.NSE"
        return clean_v
