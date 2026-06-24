import uuid
from typing import Sequence, Optional
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sync_history import SyncHistory
from app.models.enums import SyncStatus


class SyncHistoryService:
    """Manages database operations for solution synchronization history audit trails."""

    @staticmethod
    async def create_sync_record(
        db: AsyncSession,
        user_id: uuid.UUID,
        repository_id: uuid.UUID,
        problem_title: str,
        problem_slug: str,
        difficulty: str,
        language: str,
        platform: str = "leetcode"
    ) -> SyncHistory:
        """Initializes a new synchronization audit record with PENDING status."""
        record = SyncHistory(
            user_id=user_id,
            repository_id=repository_id,
            platform=platform,
            problem_title=problem_title,
            problem_slug=problem_slug,
            difficulty=difficulty.lower(),
            language=language.lower(),
            sync_status=SyncStatus.PENDING
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def update_sync_record(
        db: AsyncSession,
        sync_id: uuid.UUID,
        status: SyncStatus,
        commit_sha: Optional[str] = None,
        commit_url: Optional[str] = None,
        repository_path: Optional[str] = None,
        github_file_path: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> SyncHistory:
        """Updates synchronization status, commit metadata, or logs error details on failure."""
        result = await db.execute(select(SyncHistory).where(SyncHistory.id == sync_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError(f"Sync record with id {sync_id} not found.")

        record.sync_status = status
        record.updated_at = datetime.now(timezone.utc)

        if commit_sha is not None:
            record.commit_sha = commit_sha
        if commit_url is not None:
            record.commit_url = commit_url
        if repository_path is not None:
            record.repository_path = repository_path
        if github_file_path is not None:
            record.github_file_path = github_file_path
        if error_message is not None:
            # Truncate error message if it exceeds reasonable length
            record.error_message = error_message[:2000]

        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def get_user_sync_history(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Sequence[SyncHistory]:
        """Retrieves all synchronization history records for a User ordered by creation date descending."""
        result = await db.execute(
            select(SyncHistory)
            .where(SyncHistory.user_id == user_id)
            .order_by(SyncHistory.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_sync_by_id(
        db: AsyncSession,
        sync_id: uuid.UUID
    ) -> Optional[SyncHistory]:
        """Fetches a specific synchronization history record by unique identifier."""
        result = await db.execute(select(SyncHistory).where(SyncHistory.id == sync_id))
        return result.scalar_one_or_none()
