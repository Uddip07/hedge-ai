"""
API Schemas Package.

Exports Request, Response, and Error Pydantic models.
"""

from packages.api.schemas.error import ErrorPayload, ErrorResponse
from packages.api.schemas.request import AnalyzeStockRequest
from packages.api.schemas.response import (
    AnalyzeStockResponse,
    HealthResponse,
    RootResponse,
    VersionResponse,
)

__all__ = [
    "AnalyzeStockRequest",
    "AnalyzeStockResponse",
    "ErrorPayload",
    "ErrorResponse",
    "HealthResponse",
    "RootResponse",
    "VersionResponse",
]
