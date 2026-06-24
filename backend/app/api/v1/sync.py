import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.schemas.sync import LeetCodeSyncRequest, LeetCodeSyncResponse, SyncHistoryResponse
from app.services.leetcode_sync_service import LeetCodeSyncService
from app.services.sync_history_service import SyncHistoryService

logger = logging.getLogger("codesync.api.sync")
router = APIRouter()


@router.post("/leetcode", response_model=LeetCodeSyncResponse, status_code=status.HTTP_200_OK)
async def sync_leetcode(
    request: LeetCodeSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Synchronizes a solved LeetCode problem submission to the user's provisioned GitHub repository.

    The sync process creates/updates the problem's solution file and description README,
    updating the execution status in the database sync history audit trail.
    """
    logger.info(
        f"LeetCode sync request received from user {current_user.github_username} "
        f"for problem '{request.problem_slug}' in repository {request.repository_id}"
    )
    try:
        result = await LeetCodeSyncService.sync_leetcode_submission(
            db=db,
            user=current_user,
            request=request
        )
        return result
    except ValueError as e:
        logger.warning(f"Validation error in sync request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IntegrityError as e:
        logger.warning(
            f"Duplicate sync detection: unique constraint violated for repo {request.repository_id}, "
            f"slug '{request.problem_slug}', language '{request.language}'. Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A synchronization record for this problem and language already exists for this repository."
        )
    except HTTPException:
        # Re-raise FastAPIs HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error in sync endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during synchronization: {str(e)}"
        )


@router.get("/history", response_model=List[SyncHistoryResponse], status_code=status.HTTP_200_OK)
async def get_sync_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the synchronization history list for the current authenticated user,

    ordered by creation timestamp descending.
    """
    logger.info(f"Retrieving sync history for user {current_user.github_username}")
    try:
        history = await SyncHistoryService.get_user_sync_history(db=db, user_id=current_user.id)
        return history
    except Exception as e:
        logger.error(f"Error retrieving sync history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve synchronization history."
        )
