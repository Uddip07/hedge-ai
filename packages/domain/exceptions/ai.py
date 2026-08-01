"""
AI & Configuration Exceptions for the Indian AI Hedge Fund Domain.

Defines errors related to LLM reasoning, prompt validation, and domain setup parameters.
"""

from packages.domain.exceptions.base import DomainError


class AIError(DomainError):
    """Raised when LLM model reasoning, prompt schema, or agent execution fails."""

    DEFAULT_CODE = "AI_ERROR"


class ConfigurationError(DomainError):
    """Raised when domain configuration parameters or system environment settings are invalid."""

    DEFAULT_CODE = "CONFIGURATION_ERROR"
