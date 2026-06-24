import uuid
from sqlalchemy import Boolean, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class User(Base):
    """User model representing application users registered via GitHub OAuth."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    github_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    github_username: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False
    )

    github_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    github_avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # Note: Named encrypted to prevent accidental plaintext storage in database.
    # TODO: Implement symmetric encryption (e.g. cryptography.fernet) before production.
    github_access_token_encrypted: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Relationships
    repositories: Mapped[list["Repository"]] = relationship(
        "Repository",
        back_populates="user",
        cascade="all, delete-orphan"
    )
