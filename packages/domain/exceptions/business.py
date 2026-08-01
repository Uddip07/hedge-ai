"""
Business Rule Exceptions for the Indian AI Hedge Fund Domain.

Defines errors raised when business invariants or domain policy rules are breached.
"""

from packages.domain.exceptions.base import DomainError


class BusinessRuleViolation(DomainError):
    """Raised when an operation violates core domain business logic rules."""

    DEFAULT_CODE = "BUSINESS_RULE_VIOLATION"


class DuplicateEntityError(BusinessRuleViolation):
    """Raised when attempting to create an entity that already exists in the aggregate."""

    DEFAULT_CODE = "DUPLICATE_ENTITY"


class EntityNotFoundError(BusinessRuleViolation):
    """Raised when an entity requested by identity cannot be located in the aggregate."""

    DEFAULT_CODE = "ENTITY_NOT_FOUND"


class AuthError(DomainError):
    """Base exception for authentication and authorization errors."""

    DEFAULT_CODE = "AUTH_ERROR"


class InvalidCredentialsError(AuthError):
    """Raised when email or password authentication fails."""

    DEFAULT_CODE = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthError):
    """Raised when a JWT access or refresh token has expired."""

    DEFAULT_CODE = "TOKEN_EXPIRED"


class InvalidTokenError(AuthError):
    """Raised when a JWT token is malformed, invalid, or revoked."""

    DEFAULT_CODE = "INVALID_TOKEN"


class UnauthorizedError(AuthError):
    """Raised when an unauthenticated request attempts to access a protected resource."""

    DEFAULT_CODE = "UNAUTHORIZED"


class AccessDeniedError(AuthError):
    """Raised when an authenticated user lacks the required role or permission."""

    DEFAULT_CODE = "ACCESS_DENIED"


class UserAlreadyExistsError(AuthError):
    """Raised when attempting to register a user with an already registered email."""

    DEFAULT_CODE = "USER_ALREADY_EXISTS"


class PasswordValidationError(AuthError):
    """Raised when password policy validation fails during signup or password change."""

    DEFAULT_CODE = "PASSWORD_VALIDATION_ERROR"
