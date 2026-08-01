"""
Pydantic Schemas for Authentication and User Management.
"""

from typing import Any

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, description="User password (min 8 chars, uppercase, lowercase, digit)"
    )
    full_name: str = Field(..., min_length=1, description="User full name")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT Refresh Token")


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = 900
    user: dict[str, Any] | None = None


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(..., min_length=1, description="Updated full name")


class WatchlistRequest(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol to add/remove")


class PreferencesUpdateRequest(BaseModel):
    theme: str | None = None
    default_currency: str | None = None
    notifications_enabled: bool | None = None
    risk_tolerance: str | None = None


class SettingsUpdateRequest(BaseModel):
    mfa_enabled: bool | None = None
    session_timeout_minutes: int | None = None
    max_active_sessions: int | None = None
    api_access_enabled: bool | None = None
