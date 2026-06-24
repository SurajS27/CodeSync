import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.repository import Repository
from app.services.repository_service import RepositoryService

logger = logging.getLogger("codesync.services.access")


class RepositoryAccessService:
    """Service layer validating user access control constraints on Repository entities."""

    @staticmethod
    async def verify_repository_owner(
        db: AsyncSession,
        user_id: uuid.UUID,
        repository_id: uuid.UUID
    ) -> Repository:
        """Loads a repository and checks if the given user owns it.

        Raises:
        - HTTP 404: If the repository doesn't exist.
        - HTTP 403: If the user does not own it.
        """
        logger.debug(f"Verifying ownership of repository: {repository_id} for user: {user_id}")
        repo = await RepositoryService.get_repository_by_id(db, repository_id)

        if not repo:
            logger.warning(f"Access verification failed: Repository not found: {repository_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The requested repository was not found."
            )

        if repo.user_id != user_id:
            logger.warning(f"Access violation: User: {user_id} attempted to access repository: {repository_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this repository."
            )

        return repo
