import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import SyncStatus, DifficultyLevel


class LeetCodeSyncRequest(BaseModel):
    """Schema representing a LeetCode submission sync request."""
    repository_id: uuid.UUID
    problem_title: str = Field(..., max_length=255)
    problem_slug: str = Field(..., max_length=255)
    difficulty: DifficultyLevel
    language: str = Field(..., max_length=50)
    source_code: str = Field(..., min_length=1)
    runtime: Optional[str] = None
    memory: Optional[str] = None


class LeetCodeSyncResponse(BaseModel):
    """Schema representing the sync execution result returned to the client."""
    sync_id: uuid.UUID
    status: SyncStatus
    commit_sha: Optional[str] = None
    commit_url: Optional[str] = None
    repository_path: Optional[str] = None
    github_file_path: Optional[str] = None
    error_message: Optional[str] = None


class SyncHistoryResponse(BaseModel):
    """Schema representing a synchronization record returned from the history endpoints."""
    id: uuid.UUID
    user_id: uuid.UUID
    repository_id: uuid.UUID
    platform: str
    problem_title: str
    problem_slug: str
    difficulty: str
    language: str
    repository_path: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_url: Optional[str] = None
    sync_status: SyncStatus
    github_file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
