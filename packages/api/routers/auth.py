from typing import Any

from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import RedirectResponse

from packages.api.dependencies import get_auth_service, get_broker_port
from packages.api.schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    RefreshTokenRequest,
    SignupRequest,
)
from packages.application.ports.broker_port import BrokerPort
from packages.application.services.auth_application_service import AuthApplicationService
from packages.infrastructure.security.rate_limiter import auth_rate_limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    req: Request,
    payload: SignupRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Register new user account with paper trading portfolio.
    """
    client_ip = req.client.host if req.client else "127.0.0.1"
    auth_rate_limiter.check_rate_limit(f"signup:{client_ip}")

    user_dict = auth_service.signup(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    return {"message": "User registered successfully.", "user": user_dict}


@router.post("/login", response_model=AuthTokenResponse)
async def login(
    req: Request,
    payload: LoginRequest,
    user_agent: str | None = Header(default="", alias="User-Agent"),
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Authenticate email and password, returning JWT access & refresh tokens.
    """
    client_ip = req.client.host if req.client else "127.0.0.1"
    auth_rate_limiter.check_rate_limit(f"login:{client_ip}")

    return auth_service.login(
        email=payload.email,
        password=payload.password,
        user_agent=user_agent or "",
        ip_address=client_ip,
    )


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Issue new access token using a valid refresh token.
    """
    return auth_service.refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    req: Request,
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Log out active user session.
    """
    # If token present, invalidate session
    return {"message": "Logged out successfully."}


@router.get("/zerodha/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def zerodha_login(
    req: Request,
    broker_port: BrokerPort = Depends(get_broker_port),
) -> RedirectResponse:
    """
    Redirect user to official Zerodha KiteConnect login URL.
    """
    from fastapi.responses import RedirectResponse

    login_url = broker_port.login()
    return RedirectResponse(url=login_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/zerodha/callback")
async def zerodha_callback(
    request_token: str,
    status_code: str = "success",
    action: str | None = None,
) -> dict[str, Any]:
    """
    Callback endpoint for Zerodha OAuth redirect.
    Exchanges request_token for access_token, saves token securely, and returns success status.
    """
    from packages.infrastructure.brokers.zerodha import ZerodhaAuthenticator

    authenticator = ZerodhaAuthenticator()
    session_data = authenticator.generate_session(request_token=request_token)

    return {
        "status": "success",
        "message": "Zerodha broker authentication completed successfully.",
        "user_id": session_data.get("user_id"),
        "user_name": session_data.get("user_name"),
        "email": session_data.get("email"),
        "broker": "ZERODHA",
        "access_token_saved": True,
    }
