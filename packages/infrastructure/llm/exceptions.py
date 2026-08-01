"""
LLM Exceptions for Infrastructure Layer.

Defines exception hierarchy for LLM API invocation, provider errors, timeouts, rate limits, and JSON validation failures.
"""

from typing import Any


class LLMException(Exception):
    """Base exception for all infrastructure LLM provider errors."""

    def __init__(
        self,
        message: str,
        code: str = "LLM_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}


class LLMProviderError(LLMException):
    """Raised when the LLM provider API returns an error or fails to respond."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="LLM_PROVIDER_ERROR", context=context)


class LLMTimeoutError(LLMException):
    """Raised when an LLM API call times out."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="LLM_TIMEOUT_ERROR", context=context)


class LLMRateLimitError(LLMException):
    """Raised when an LLM API rate limit or quota is exceeded."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="LLM_RATE_LIMIT_ERROR", context=context)


class LLMValidationError(LLMException):
    """Raised when LLM output fails JSON parsing or response schema validation."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="LLM_VALIDATION_ERROR", context=context)


class LLMConfigurationError(LLMException):
    """Raised when provider configuration or API keys are missing or invalid."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="LLM_CONFIG_ERROR", context=context)


class LLMContextLengthExceededError(LLMException):
    """Raised when prompt text exceeds provider max context window capacity."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="LLM_CONTEXT_LENGTH_ERROR", context=context)
