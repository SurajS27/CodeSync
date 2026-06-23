import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger("codesync.services.user")


class UserService:
    """Service layer class handling database actions for the User entity."""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
        """Fetch a user record by its primary key ID."""
        logger.debug(f"Fetching user by ID: {user_id}")
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_github_id(db: AsyncSession, github_id: str) -> User | None:
        """Fetch a user record by their unique GitHub account ID."""
        logger.debug(f"Fetching user by GitHub ID: {github_id}")
        result = await db.execute(select(User).where(User.github_id == github_id))
        return result.scalars().first()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_in: UserCreate,
        github_access_token_encrypted: str | None = None
    ) -> User:
        """Create and store a new User database entry from registration info."""
        logger.info(f"Creating user profile for GitHub user: {user_in.github_username}")
        # Build the SQLAlchemy database model from schema fields
        db_user = User(
            github_id=user_in.github_id,
            github_username=user_in.github_username,
            github_email=user_in.github_email,
            github_avatar_url=str(user_in.github_avatar_url) if user_in.github_avatar_url else None,
            github_access_token_encrypted=github_access_token_encrypted,
            is_active=user_in.is_active
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def update_github_access_token(
        db: AsyncSession,
        user_id: uuid.UUID,
        github_access_token_encrypted: str
    ) -> User | None:
        """Update the stored OAuth token for a specific user."""
        logger.info(f"Updating GitHub access token for user ID: {user_id}")
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found for token update: {user_id}")
            return None

        user.github_access_token_encrypted = github_access_token_encrypted
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
