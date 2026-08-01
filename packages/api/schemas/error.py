"""
Standard Error Response Schemas for MONEYYYYYY API.

Formats error responses into consistent JSON envelopes.
"""

from typing import Any

from pydantic import BaseModel, Field


class ErrorPayload(BaseModel):
    """
    Standard error payload body.
    """

    code: str = Field(..., description="Unique error classification code string.")
    message: str = Field(..., description="Human-readable error summary message.")
    details: Any = Field(
        default=None,
        description="Optional structured error diagnostic details or validation errors.",
    )


class ErrorResponse(BaseModel):
    """
    Top-level error response envelope wrapping ErrorPayload.
    """

    error: ErrorPayload


class StandardErrorSchema(BaseModel):
    """Standardized API Error Response Schema."""

    code: str = Field(..., description="Error classification string.")
    message: str = Field(..., description="User-facing error message.")
    details: dict[str, Any] | None = Field(default=None, description="Diagnostic context.")
    request_id: str | None = Field(default=None, description="Trace request UUID.")
    timestamp: str | None = Field(default=None, description="ISO error timestamp.")


class ValidationErrorSchema(BaseModel):
    """Validation Error Schema (422 Unprocessable Entity)."""

    code: str = Field(default="VALIDATION_ERROR")
    message: str = Field(default="Request payload or parameter validation failed.")
    validation_errors: list[dict[str, Any]] = Field(default_factory=list)


class BusinessErrorSchema(BaseModel):
    """Business Domain Rule Error Schema (400 / 422)."""

    code: str = Field(default="BUSINESS_RULE_VIOLATION")
    message: str = Field(..., description="Domain business rule failure details.")
    domain_context: dict[str, Any] = Field(default_factory=dict)


class AuthenticationErrorSchema(BaseModel):
    """Authentication Error Schema (401 Unauthorized)."""

    code: str = Field(default="UNAUTHENTICATED")
    message: str = Field(default="Authentication credentials missing or invalid.")


class AuthorizationErrorSchema(BaseModel):
    """Authorization Error Schema (403 Forbidden)."""

    code: str = Field(default="UNAUTHORIZED")
    message: str = Field(default="Insufficient permissions to access resource.")


class ProviderErrorSchema(BaseModel):
    """Third-Party Infrastructure Provider Error Schema (502 / 504)."""

    code: str = Field(default="PROVIDER_ERROR")
    message: str = Field(..., description="Provider connection or execution failure.")
    provider_name: str = Field(..., description="Upstream vendor name.")
    execution_status: str = Field(default="FAILED")


class InternalErrorSchema(BaseModel):
    """Internal Server Error Schema (500 Internal Server Error)."""

    code: str = Field(default="INTERNAL_SERVER_ERROR")
    message: str = Field(default="An unexpected internal server error occurred.")
