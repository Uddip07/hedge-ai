import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerifyMismatchError,
)

from packages.domain.exceptions.business import (
    InvalidTokenError,
    TokenExpiredError,
)

_auth_logger = logging.getLogger("ihf_ai.infrastructure.security.auth")

ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

_INSECURE_FALLBACK_SECRET = "dev-only-secret-DO-NOT-USE-IN-PRODUCTION"
_raw_secret = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

if not _raw_secret:
    environment = os.environ.get("APP_ENVIRONMENT", "development").lower()
    if environment == "production":
        raise RuntimeError("JWT_SECRET_KEY must be set in production environments")
    _raw_secret = _INSECURE_FALLBACK_SECRET
    _auth_logger.warning(
        "JWT_SECRET_KEY is not set in environment — using insecure development fallback. "
        "Set the JWT_SECRET_KEY environment variable before deploying to production."
    )
JWT_SECRET_KEY: str = _raw_secret


def hash_password(password: str) -> str:
    """Hash plain text password using Argon2id."""
    return str(ph.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain text password against Argon2id hash."""
    try:
        return bool(ph.verify(hashed_password, plain_password))
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(user_id: str, role: str, expires_delta: timedelta | None = None) -> str:
    """Create signed JWT access token."""
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return str(jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM))


def create_refresh_token(
    user_id: str, session_id: str, expires_delta: timedelta | None = None
) -> str:
    """Create signed JWT refresh token."""
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    payload = {
        "sub": user_id,
        "sid": session_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return str(jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM))


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT payload."""
    try:
        res = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return dict(res)
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Token has expired.") from exc
    except jwt.PyJWTError as exc:
        raise InvalidTokenError("Token payload is invalid or malformed.") from exc
