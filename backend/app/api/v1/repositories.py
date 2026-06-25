import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.models.enums import BootstrapStatus
from app.models.user import User
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryCreateResponse,
    RepositoryResponse,
)
from app.services.github_repository_service import GitHubRepositoryService
from app.services.repository_access_service import RepositoryAccessService
from app.services.repository_bootstrap_service import RepositoryBootstrapService
from app.services.repository_service import RepositoryService

logger = logging.getLogger("codesync.api.repositories")
router = APIRouter()


@router.post(
    "/create",
    response_model=RepositoryCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_repository(
    repo_in: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Provisions a GitHub repository for synchronizing solutions.

    Checks if it exists in local DB and GitHub. If it does not exist,
    provisions it on GitHub, saves metadata in Neon DB, and automatically
    bootstraps the repository layout. Returns details of the bootstrap outcome.
    """
    logger.info(
        f"Repository creation request received from user: {current_user.github_username}"
    )

    # 1. Check local database
    db_repo = await RepositoryService.get_repository_by_name(
        db, current_user.id, repo_in.repo_name
    )

    # 2. Check GitHub API
    github_exists = await GitHubRepositoryService.check_github_repository_exists(
        current_user, repo_in.repo_name
    )

    if db_repo and github_exists:
        logger.info(
            f"Repository '{repo_in.repo_name}' already exists in DB and GitHub. Returning existing."
        )
        # If it was previously failed, we can return the failed status
        return {
            "repository": db_repo,
            "bootstrap_status": db_repo.bootstrap_status,
            "message": "Repository already exists.",
        }

    if github_exists:
        # Exists on GitHub, but not in DB. Import it and trigger bootstrap if needed.
        logger.info(
            f"Repository '{repo_in.repo_name}' exists on GitHub but not in database. Importing metadata."
        )
        repo_data = await GitHubRepositoryService.fetch_github_repository_details(
            current_user, repo_in.repo_name
        )

        github_created = datetime.fromisoformat(
            repo_data["created_at"].replace("Z", "+00:00")
        )
        github_updated = datetime.fromisoformat(
            repo_data["updated_at"].replace("Z", "+00:00")
        )

        new_repo_data = {
            "github_repo_id": repo_data["id"],
            "repo_name": repo_data["name"],
            "repo_full_name": repo_data["full_name"],
            "repo_url": repo_data["html_url"],
            "owner_github_username": repo_data["owner"]["login"],
            "default_branch": repo_data["default_branch"],
            "is_private": repo_data["private"],
            "github_created_at": github_created,
            "github_updated_at": github_updated,
        }

        if db_repo:
            new_repo = await RepositoryService.update_repository_record(
                db, db_repo.id, new_repo_data
            )
        else:
            new_repo = await RepositoryService.create_repository_record(
                db, current_user.id, new_repo_data
            )

        # Trigger bootstrap on imported repository
        try:
            await RepositoryBootstrapService.bootstrap_repository(
                db, current_user, new_repo
            )
            await db.refresh(new_repo)
            return {
                "repository": new_repo,
                "bootstrap_status": BootstrapStatus.COMPLETED,
                "message": "Repository created and bootstrapped successfully.",
            }
        except Exception as e:
            logger.error(
                f"Failed to bootstrap imported repository '{new_repo.repo_full_name}': {str(e)}"
            )
            await db.refresh(new_repo)
            return {
                "repository": new_repo,
                "bootstrap_status": BootstrapStatus.FAILED,
                "message": "Repository created successfully, but bootstrap failed.",
            }

    # 3. Provision new repository on GitHub (resolving name clashes)
    unique_name = await GitHubRepositoryService.generate_unique_repository_name(
        db, current_user, repo_in.repo_name
    )
    logger.info(f"Unique candidate name resolved: {unique_name}")

    github_data = await GitHubRepositoryService.create_github_repository(
        current_user, unique_name, repo_in.is_private
    )

    # 4. Save metadata to Neon DB
    github_created = datetime.fromisoformat(
        github_data["created_at"].replace("Z", "+00:00")
    )
    github_updated = datetime.fromisoformat(
        github_data["updated_at"].replace("Z", "+00:00")
    )

    new_repo_data = {
        "github_repo_id": github_data["id"],
        "repo_name": github_data["name"],
        "repo_full_name": github_data["full_name"],
        "repo_url": github_data["html_url"],
        "owner_github_username": github_data["owner"]["login"],
        "default_branch": github_data["default_branch"],
        "is_private": github_data["private"],
        "github_created_at": github_created,
        "github_updated_at": github_updated,
    }

    if db_repo:
        new_repo = await RepositoryService.update_repository_record(
            db, db_repo.id, new_repo_data
        )
    else:
        new_repo = await RepositoryService.create_repository_record(
            db, current_user.id, new_repo_data
        )

    # 5. Automatically invoke Bootstrapping workflow
    try:
        await RepositoryBootstrapService.bootstrap_repository(
            db, current_user, new_repo
        )
        await db.refresh(new_repo)
        return {
            "repository": new_repo,
            "bootstrap_status": BootstrapStatus.COMPLETED,
            "message": "Repository created and bootstrapped successfully.",
        }
    except Exception as e:
        logger.error(
            f"Post-creation auto-bootstrap failed for repository '{new_repo.repo_full_name}': {str(e)}"
        )
        await db.refresh(new_repo)
        return {
            "repository": new_repo,
            "bootstrap_status": BootstrapStatus.FAILED,
            "message": "Repository created successfully, but bootstrap failed.",
        }


@router.post("/{repository_id}/bootstrap", status_code=status.HTTP_200_OK)
async def bootstrap_repository_manually(
    repository_id: uuid.UUID,
    force: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Allows manually triggering/re-triggering the structural bootstrap process.

    Enforces ownership validation checks. Supports `?force=true` query parameters.
    """
    repo = await RepositoryAccessService.verify_repository_owner(
        db, current_user.id, repository_id
    )
    try:
        await RepositoryBootstrapService.bootstrap_repository(
            db, current_user, repo, force=force
        )
        return {"message": "Repository successfully initialized and bootstrapped."}
    except Exception as e:
        logger.error(f"Manual bootstrap process failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Bootstrap failed due to GitHub API error: {str(e)}",
        )


@router.get("", response_model=list[RepositoryResponse])
async def list_repositories(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Lists all configured repository solutions associated with the authenticated User."""
    return await RepositoryService.get_user_repositories(db, current_user.id)


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository_details(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetches details of a specific configured repository solution.

    Enforces ownership validation checks.
    """
    repo = await RepositoryAccessService.verify_repository_owner(
        db, current_user.id, repository_id
    )
    return repo


@router.delete("/{repository_id}", status_code=status.HTTP_200_OK)
async def delete_repository(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a configured repository solution mapping from CodeSync local database.

    Note: This does not delete the repository from GitHub.
    # TODO: Add optional parameter and logic to support deletion from GitHub in a future milestone.
    """
    await RepositoryAccessService.verify_repository_owner(
        db, current_user.id, repository_id
    )
    deleted = await RepositoryService.delete_repository_record(db, repository_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove repository metadata from database.",
        )

    return {"message": "Repository removed successfully from CodeSync database."}
