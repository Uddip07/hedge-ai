"""
Domain Exceptions Package for the Indian AI Hedge Fund Platform.

Consolidates all domain error classes deriving from DomainError.
"""

from packages.domain.exceptions.ai import AIError, ConfigurationError
from packages.domain.exceptions.base import DomainError
from packages.domain.exceptions.business import (
    AccessDeniedError,
    AuthError,
    BusinessRuleViolation,
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidCredentialsError,
    InvalidTokenError,
    PasswordValidationError,
    TokenExpiredError,
    UnauthorizedError,
    UserAlreadyExistsError,
)
from packages.domain.exceptions.execution import BrokerError, ExecutionError
from packages.domain.exceptions.market import (
    CorporateActionError,
    MarketError,
    SettlementError,
)
from packages.domain.exceptions.portfolio import InsufficientFundsError, PortfolioError
from packages.domain.exceptions.research import (
    KnowledgeError,
    ResearchError,
    StrategyError,
)
from packages.domain.exceptions.risk import RiskViolation
from packages.domain.exceptions.validation import (
    ISINValidationError,
    OrderValidationError,
    PositionValidationError,
    TickerValidationError,
    ValidationError,
)

__all__ = [
    # Base Error
    "DomainError",
    # Validation Errors
    "ValidationError",
    "OrderValidationError",
    "PositionValidationError",
    "TickerValidationError",
    "ISINValidationError",
    # Business Errors
    "BusinessRuleViolation",
    "DuplicateEntityError",
    "EntityNotFoundError",
    # Auth Errors
    "AuthError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "InvalidTokenError",
    "UnauthorizedError",
    "AccessDeniedError",
    "UserAlreadyExistsError",
    "PasswordValidationError",
    # Market Errors
    "MarketError",
    "CorporateActionError",
    "SettlementError",
    # Portfolio Errors
    "PortfolioError",
    "InsufficientFundsError",
    # Execution Errors
    "ExecutionError",
    "BrokerError",
    # Risk Errors
    "RiskViolation",
    # Research Errors
    "ResearchError",
    "StrategyError",
    "KnowledgeError",
    # AI & Config Errors
    "AIError",
    "ConfigurationError",
]
