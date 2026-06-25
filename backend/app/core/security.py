import logging
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.services.oauth_state_service import OAuthStateService

logger = logging.getLogger("codesync.security")


def create_access_token(user_id: str, github_id: str) -> str:
    """Generates a HS256 signed JWT for the authenticated user."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "sub": str(user_id),
        "github_id": github_id,
        "exp": int(expire.timestamp()),
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str) -> dict | None:
    """Decodes and validates a JWT access token, returning its payload if valid."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT validation failed: Token signature has expired.")
        return None
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        return None


def create_oauth_state() -> str:
    """Generates a transient security state parameter."""
    return OAuthStateService.create_state()


def verify_oauth_state(client_state: str, expected_state: str) -> bool:
    """Validates the client-provided state parameter against expected state and active store."""
    if not client_state or not expected_state:
        return False
    if client_state != expected_state:
        logger.warning("OAuth State mismatch detected.")
        return False
    # Validate token lifecycle & enforce single-use
    return OAuthStateService.validate_state(client_state)
