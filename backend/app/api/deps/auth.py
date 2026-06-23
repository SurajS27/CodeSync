import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.core.security import verify_access_token
from app.models.user import User
from app.services.user_service import UserService

# Enforce JWT HTTP Bearer authorization scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency injection helper to validate JWT access tokens and yield the authenticated User."""
    token = credentials.credentials
    payload = verify_access_token(token)

    # 1. Invalid or expired token checks
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid or has expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 2. Extract canonical identity claim (sub)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing canonical identity claim.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token contains malformed identity claim.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 3. Load user record from database
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account associated with this token was not found."
        )

    # 4. Check user status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user account is currently inactive."
        )

    return user
