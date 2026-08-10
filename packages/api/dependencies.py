from functools import lru_cache
from typing import Any

from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.ai.committee import IntelligentInvestmentCommittee
from packages.api.config import APIConfig
from packages.application.company_intelligence import CompanyIntelligenceOrchestrator
from packages.application.ports.broker_port import BrokerPort
from packages.application.ports.market_data_port import MarketDataPort
from packages.application.services import AuthApplicationService, ResearchApplicationService
from packages.application.use_cases import AnalyzeStockUseCase
from packages.domain.enums.system import UserRole
from packages.domain.exceptions.business import AccessDeniedError, UnauthorizedError
from packages.domain.user.user import User
from packages.domain.value_objects.identifiers.uuid_wrappers import UserId
from packages.infrastructure.dependency_injection import DIContainer
from packages.infrastructure.security.auth import decode_token

security_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_container() -> DIContainer:
    """Return singleton instance of Infrastructure DIContainer."""
    return DIContainer()


def get_analyze_stock_use_case(
    container: DIContainer = Depends(get_container),
) -> AnalyzeStockUseCase:
    """Dependency provider for AnalyzeStockUseCase."""
    return container.analyze_stock_use_case


def get_research_service(
    container: DIContainer = Depends(get_container),
) -> ResearchApplicationService:
    """Dependency provider for ResearchApplicationService."""
    return container.research_service


def get_auth_service(
    container: DIContainer = Depends(get_container),
) -> AuthApplicationService:
    """Dependency provider for AuthApplicationService."""
    return container.auth_service


def get_market_data_port(
    container: DIContainer = Depends(get_container),
) -> MarketDataPort:
    """Dependency provider for MarketDataPort."""
    return container.market_data_port


def get_broker_port(
    container: DIContainer = Depends(get_container),
) -> BrokerPort:
    """Dependency provider for BrokerPort."""
    return container.broker_port


@lru_cache
def get_company_intelligence_orchestrator() -> CompanyIntelligenceOrchestrator:
    """Dependency provider for CompanyIntelligenceOrchestrator."""
    return CompanyIntelligenceOrchestrator()


@lru_cache
def get_investment_committee() -> IntelligentInvestmentCommittee:
    """Dependency provider for IntelligentInvestmentCommittee."""
    return IntelligentInvestmentCommittee()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> User:
    """Validate HTTP Bearer token and return active User aggregate."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedError("Missing or invalid HTTP Authorization Bearer token.")

    token = credentials.credentials
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError("Provided token is not an access token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Access token payload missing sub claim.")

    user = auth_service.user_repo.get_by_id(UserId.from_str(user_id_str))
    if not user or not user.is_active:
        raise UnauthorizedError("User account disabled or not found.")

    return user


def require_role(required_role: UserRole) -> Any:
    """Dependency factory enforcing role-based access control."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise AccessDeniedError(
                f"Requires '{required_role.value}' role privileges.",
                context={"required": required_role.value, "actual": current_user.role.value},
            )
        return current_user

    return role_checker


async def verify_automation_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    auth_credentials: HTTPAuthorizationCredentials | None = Security(security_bearer),
) -> bool:
    """
    Validate automation API key supplied via X-API-Key or Bearer token header.
    Secures n8n orchestration triggers and external webhook calls.
    """
    cfg = APIConfig()
    expected_key = cfg.automation_api_key

    provided_key: str | None = None
    if x_api_key:
        provided_key = x_api_key.strip()
    elif auth_credentials and auth_credentials.credentials:
        provided_key = auth_credentials.credentials.strip()

    if not provided_key or provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing automation API Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return True
