"""
Response Schemas for MONEYYYYYY API endpoints.
"""

from typing import Any

from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    """
    Root status response for GET /.
    """

    application: str = Field(default="MONEYYYYYY")
    version: str = Field(default="1.0.0")
    status: str = Field(default="running")


class HealthResponse(BaseModel):
    """
    Health check response for GET /health.
    """

    status: str = Field(default="healthy")
    database: str = Field(default="production")
    cache: str = Field(default="production")
    application: str = Field(default="running")


class VersionResponse(BaseModel):
    """
    Version metadata response for GET /version.
    """

    name: str = Field(default="MONEYYYYYY API")
    version: str = Field(default="1.0.0")
    environment: str = Field(default="production")
    build: dict[str, Any] = Field(
        default_factory=lambda: {
            "python_version": "3.12",
            "architecture": "Clean Architecture",
            "release_candidate": "v1.0.0-rc1",
        }
    )


class AnalyzeStockResponse(BaseModel):
    """
    Response model wrapping single-stock analysis output.
    """

    ticker: str
    recommendation: str
    consensus_score: float
    risk_level: str
    is_suitable_for_portfolio: bool
    reasoning_summary: str
    analyzed_at: str


class EvaluateCommitteeResponse(BaseModel):
    """
    Response model wrapping Intelligent Investment Committee evaluation output.
    """

    decision_id: str
    session_id: str
    ticker: str
    winning_recommendation: str
    consensus_score: float
    confidence: float
    agreement_ratio: float
    verdict_summary: str
    audit_signature: str
    timestamp: str
    explanation: dict[str, Any]


class CompanyIntelligenceResponse(BaseModel):
    """
    Response model wrapping end-to-end Company Intelligence research report.
    """

    ticker: str
    company_name: str
    session_id: str
    timestamp: str
    executive_summary: dict[str, Any]
    market_snapshot: dict[str, Any]
    financial_highlights: dict[str, Any]
    technical_analysis: dict[str, Any]
    news_section: dict[str, Any]
    corporate_actions: dict[str, Any]
    macro_context: dict[str, Any]
    agent_opinions: dict[str, Any]
    consensus_decision: dict[str, Any]
    explainability: dict[str, Any]
    bull_case: list[str]
    bear_case: list[str]
