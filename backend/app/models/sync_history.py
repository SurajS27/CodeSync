import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import SyncStatus

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.user import User


class SyncHistory(Base):
    """Tracks synchronization status and history of coding platform submissions to GitHub."""

    __tablename__ = "sync_history"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50), default="leetcode", nullable=False
    )

    problem_title: Mapped[str] = mapped_column(String(255), nullable=False)

    problem_slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)

    language: Mapped[str] = mapped_column(String(50), nullable=False)

    repository_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    commit_sha: Mapped[str | None] = mapped_column(String(100), nullable=True)

    commit_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    sync_status: Mapped[SyncStatus] = mapped_column(
        SQLEnum(
            SyncStatus,
            name="syncstatus",
            values_callable=lambda x: [e.value for e in x],
            create_type=False,
        ),
        default=SyncStatus.PENDING,
        nullable=False,
        index=True,
    )

    github_file_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship()
    repository: Mapped["Repository"] = relationship()

    # Table Constraints
    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "problem_slug",
            "language",
            name="uq_sync_history_repo_slug_lang",
        ),
    )
