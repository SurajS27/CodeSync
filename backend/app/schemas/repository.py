import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BootstrapStatus


class RepositoryBase(BaseModel):
    """Base fields for repository schemas."""

    repo_name: str = Field(
        ..., max_length=255, description="Name of the GitHub repository"
    )
    is_private: bool = Field(
        default=True, description="Whether the repository should be private"
    )


class RepositoryCreate(RepositoryBase):
    """Schema for repository provisioning request."""

    pass


class RepositoryResponse(BaseModel):
    """Schema for responding with repository metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    repo_name: str
    repo_full_name: str
    repo_url: str
    owner_github_username: str
    default_branch: str
    is_private: bool
    is_sync_enabled: bool
    bootstrapped_at: datetime | None
    bootstrap_version: str | None
    bootstrap_status: BootstrapStatus
    bootstrap_error: str | None
    last_bootstrap_attempt_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RepositoryCreateResponse(BaseModel):
    """Response schema returned after repository creation, detailing bootstrapping outcomes."""

    repository: RepositoryResponse
    bootstrap_status: BootstrapStatus
    message: str
