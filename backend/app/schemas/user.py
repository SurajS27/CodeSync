import uuid
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Base fields for User schemas."""

    github_id: str = Field(..., max_length=255, description="Unique GitHub User ID")
    github_username: str = Field(..., max_length=255, description="GitHub Username")
    github_email: str | None = Field(
        None, max_length=255, description="Primary email address on GitHub"
    )
    github_avatar_url: AnyHttpUrl | None = Field(
        None, description="GitHub user profile avatar URL"
    )
    is_active: bool = Field(
        default=True, description="Indicates if the user account is active"
    )


class UserCreate(UserBase):
    """Schema for creating a new user record.

    Add any authentication-specific payload details here if needed later.
    """

    pass


class UserResponse(UserBase):
    """Schema for responding with serialized User data.

    Excludes github_access_token_encrypted to prevent leakage.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
