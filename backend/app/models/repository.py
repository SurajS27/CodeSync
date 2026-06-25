import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import BootstrapStatus

if TYPE_CHECKING:
    from app.models.user import User


class Repository(Base):
    """Repository model representing GitHub repositories configured for LeetCode solution sync."""

    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    github_repo_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )

    repo_name: Mapped[str] = mapped_column(String(255), nullable=False)

    repo_full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    repo_url: Mapped[str] = mapped_column(String(500), nullable=False)

    owner_github_username: Mapped[str] = mapped_column(String(255), nullable=False)

    default_branch: Mapped[str] = mapped_column(String(100), nullable=False)

    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False)

    is_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    leetcode_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    last_sync_status: Mapped[str | None] = mapped_column(String(100), nullable=True)

    github_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    github_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Bootstrapping metadata
    bootstrapped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    bootstrap_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    bootstrap_status: Mapped[BootstrapStatus] = mapped_column(
        SQLEnum(
            BootstrapStatus,
            name="bootstrapstatus",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=BootstrapStatus.PENDING,
        nullable=False,
    )

    bootstrap_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    last_bootstrap_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="repositories")

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "repo_name", name="uq_repositories_user_repo"),
    )
