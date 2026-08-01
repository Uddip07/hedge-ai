"""
Global Exception Handlers for MONEYYYYYY API.

Formats exceptions into standard JSON error responses:
{
    "error": {
        "code": "...",
        "message": "...",
        "details": ...
    }
}
"""

import json
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from packages.application.exceptions import (
    ApplicationException,
    EntityNotFoundApplicationError,
    ValidationApplicationError,
)
from packages.domain.exceptions import DomainError, ValidationError
from packages.domain.exceptions.business import (
    AccessDeniedError,
    InvalidCredentialsError,
    InvalidTokenError,
    PasswordValidationError,
    TokenExpiredError,
    UnauthorizedError,
    UserAlreadyExistsError,
)
from packages.infrastructure.security.rate_limiter import RateLimitExceededError


def _to_json_safe(obj: Any) -> Any:
    """Recursively convert details payload to JSON-serializable primitives."""
    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return str(obj)


async def application_exception_handler(
    request: Request, exc: ApplicationException
) -> JSONResponse:
    """Handle domain/application layer exceptions."""
    if isinstance(exc, EntityNotFoundApplicationError):
        http_status = status.HTTP_404_NOT_FOUND
        code = "ENTITY_NOT_FOUND"
    elif isinstance(exc, ValidationApplicationError):
        http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        code = "VALIDATION_ERROR"
    else:
        http_status = status.HTTP_400_BAD_REQUEST
        code = "APPLICATION_ERROR"

    return JSONResponse(
        status_code=http_status,
        content={
            "error": {
                "code": code,
                "message": exc.message,
                "details": _to_json_safe(getattr(exc, "context", None)),
            }
        },
    )


async def domain_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle domain validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "DOMAIN_VALIDATION_ERROR",
                "message": str(exc),
                "details": None,
            }
        },
    )


async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Handle generic domain errors and mapped auth errors."""
    code = getattr(exc, "code", "DOMAIN_ERROR")

    if isinstance(
        exc, (UnauthorizedError, TokenExpiredError, InvalidTokenError, InvalidCredentialsError)
    ):
        http_status = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AccessDeniedError):
        http_status = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, (UserAlreadyExistsError, PasswordValidationError)):
        http_status = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, RateLimitExceededError):
        http_status = status.HTTP_429_TOO_MANY_REQUESTS
    else:
        http_status = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=http_status,
        content={
            "error": {
                "code": code,
                "message": getattr(exc, "message", str(exc)),
                "details": _to_json_safe(getattr(exc, "context", None)),
            }
        },
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI / Pydantic request validation errors."""
    errors = exc.errors()
    msg = "Request validation failed."
    if errors and len(errors) > 0:
        first_err = errors[0]
        msg = f"{first_err.get('msg', 'Invalid field')} at {'.'.join(str(loc) for loc in first_err.get('loc', []))}"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "REQUEST_VALIDATION_ERROR",
                "message": msg,
                "details": _to_json_safe(errors),
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "details": None,
            }
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled internal exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": str(exc),
            }
        },
    )
