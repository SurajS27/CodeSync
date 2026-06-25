import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository import Repository

logger = logging.getLogger("codesync.services.repository")


class RepositoryService:
    """Service layer class handling database CRUD operations for the Repository entity."""

    @staticmethod
    async def get_repository_by_id(
        db: AsyncSession, repo_id: uuid.UUID
    ) -> Repository | None:
        """Fetch a repository record by its primary key ID."""
        logger.debug(f"Fetching repository by ID: {repo_id}")
        result = await db.execute(select(Repository).where(Repository.id == repo_id))
        return result.scalars().first()

    @staticmethod
    async def get_repository_by_name(
        db: AsyncSession, user_id: uuid.UUID, repo_name: str
    ) -> Repository | None:
        """Fetch a repository record by user ownership and name (Unique constraint checks)."""
        logger.debug(f"Fetching repository by name: {repo_name} for user: {user_id}")
        result = await db.execute(
            select(Repository).where(
                Repository.user_id == user_id, Repository.repo_name == repo_name
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_user_repositories(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[Repository]:
        """Fetch all repository records associated with a specific user."""
        logger.debug(f"Fetching all repositories for user: {user_id}")
        result = await db.execute(
            select(Repository).where(Repository.user_id == user_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_repository_record(
        db: AsyncSession, user_id: uuid.UUID, repo_data: dict
    ) -> Repository:
        """Inserts a new repository metadata record into the database."""
        logger.info(
            f"Creating repository metadata record for name: {repo_data.get('repo_name')}"
        )
        db_repo = Repository(
            user_id=user_id,
            github_repo_id=repo_data["github_repo_id"],
            repo_name=repo_data["repo_name"],
            repo_full_name=repo_data["repo_full_name"],
            repo_url=repo_data["repo_url"],
            owner_github_username=repo_data["owner_github_username"],
            default_branch=repo_data["default_branch"],
            is_private=repo_data["is_private"],
            github_created_at=repo_data.get("github_created_at"),
            github_updated_at=repo_data.get("github_updated_at"),
        )
        db.add(db_repo)
        await db.commit()
        await db.refresh(db_repo)
        return db_repo

    @staticmethod
    async def update_repository_record(
        db: AsyncSession, repo_id: uuid.UUID, update_data: dict
    ) -> Repository | None:
        """Updates an existing repository record with new settings/metadata."""
        logger.info(f"Updating repository record: {repo_id}")
        repo = await RepositoryService.get_repository_by_id(db, repo_id)
        if not repo:
            logger.warning(f"Repository not found for update: {repo_id}")
            return None

        # Update columns dynamically
        for key, value in update_data.items():
            if hasattr(repo, key):
                setattr(repo, key, value)

        db.add(repo)
        await db.commit()
        await db.refresh(repo)
        return repo

    @staticmethod
    async def delete_repository_record(db: AsyncSession, repo_id: uuid.UUID) -> bool:
        """Removes a repository metadata record from the database."""
        logger.info(f"Deleting repository record: {repo_id}")
        repo = await RepositoryService.get_repository_by_id(db, repo_id)
        if not repo:
            logger.warning(f"Repository not found for deletion: {repo_id}")
            return False

        await db.delete(repo)
        await db.commit()
        return True
