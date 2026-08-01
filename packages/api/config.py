"""
API Layer Configuration Settings.

Encapsulates FastAPI app metadata, title, version, documentation endpoints, and CORS.
"""

import os
from dataclasses import dataclass, field


def _default_allowed_origins() -> list[str]:
    raw_value = os.getenv("CORS_ALLOWED_ORIGINS", "*").strip()
    if not raw_value or raw_value == "*":
        return ["*"]
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


@dataclass(frozen=True)
class APIConfig:
    """
    Configuration parameters for FastAPI application setup.

    Attributes:
        title (str): Application title ("MONEYYYYYY API").
        version (str): Application version ("0.1.0").
        description (str): OpenAPI platform description.
        docs_url (str): Swagger UI path ("/docs").
        redoc_url (str): ReDoc path ("/redoc").
        openapi_url (str): OpenAPI schema path ("/openapi.json").
        allowed_origins (list[str]): Allowed CORS origins list.
    """

    title: str = field(default_factory=lambda: os.getenv("APP_API_TITLE", "MONEYYYYYY API"))
    version: str = field(default_factory=lambda: os.getenv("APP_API_VERSION", "0.1.0"))
    description: str = field(
        default_factory=lambda: os.getenv(
            "APP_API_DESCRIPTION",
            "Institutional-Grade Multi-Agent AI Investment Research & Execution Platform for Indian Markets",
        )
    )
    docs_url: str = field(default_factory=lambda: os.getenv("APP_API_DOCS_URL", "/docs"))
    redoc_url: str = field(default_factory=lambda: os.getenv("APP_API_REDOC_URL", "/redoc"))
    openapi_url: str = field(
        default_factory=lambda: os.getenv("APP_API_OPENAPI_URL", "/openapi.json")
    )
    allowed_origins: list[str] = field(default_factory=_default_allowed_origins)
