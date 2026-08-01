from typing import Any

from fastapi import APIRouter, Depends

from packages.api.dependencies import get_auth_service, get_current_user, require_role
from packages.api.schemas.auth import (
    PreferencesUpdateRequest,
    SettingsUpdateRequest,
    UpdateProfileRequest,
    WatchlistRequest,
)
from packages.application.services.auth_application_service import AuthApplicationService
from packages.domain.enums.system import UserRole
from packages.domain.user.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """
    Retrieve authenticated user profile and owned resources.
    """
    return current_user.to_dict()


@router.put("/me")
async def update_my_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Update user profile metadata.
    """
    updated = auth_service.update_user_profile(current_user.id, full_name=payload.full_name)
    return updated.to_dict()


@router.get("/me/watchlist")
async def get_watchlist(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """
    Retrieve user watchlist tickers.
    """
    return {"watchlist": current_user.watchlist}


@router.post("/me/watchlist")
async def add_to_watchlist(
    payload: WatchlistRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Add symbol to user watchlist.
    """
    updated = auth_service.add_watchlist(current_user.id, payload.symbol)
    return {"watchlist": updated.watchlist}


@router.delete("/me/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Remove symbol from user watchlist.
    """
    updated = auth_service.remove_watchlist(current_user.id, symbol)
    return {"watchlist": updated.watchlist}


@router.put("/me/preferences")
async def update_preferences(
    payload: PreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Update user preferences.
    """
    data = payload.model_dump(exclude_unset=True)
    updated = auth_service.update_preferences(current_user.id, data)
    return updated.preferences.to_dict()


@router.put("/me/settings")
async def update_settings(
    payload: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Update user settings.
    """
    data = payload.model_dump(exclude_unset=True)
    updated = auth_service.update_settings(current_user.id, data)
    return updated.settings.to_dict()


@router.get("/admin/users", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def list_users_admin(
    auth_service: AuthApplicationService = Depends(get_auth_service),
) -> dict[str, Any]:
    """
    Admin-only endpoint listing all platform users.
    """
    users = auth_service.user_repo.list_all()
    return {"users": [u.to_dict() for u in users]}
