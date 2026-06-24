import logging
from datetime import datetime
import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.repository_service import RepositoryService
from app.utils.encryption import decrypt_token

logger = logging.getLogger("codesync.services.github_repository")


class GitHubRepositoryService:
    """Asynchronous client service interfacing with GitHub API for repository configuration."""

    @staticmethod
    async def check_github_repository_exists(user: User, repo_name: str) -> bool:
        """Queries GitHub to check if a repository already exists under user's namespace."""
        if not user.github_access_token_encrypted:
            return False

        token = decrypt_token(user.github_access_token_encrypted)
        owner = user.github_username
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "CodeSync-Backend"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                logger.info(f"Repository {owner}/{repo_name} verified as existing on GitHub.")
                return True
            return False

    @staticmethod
    async def generate_unique_repository_name(
        db: AsyncSession,
        user: User,
        base_name: str
    ) -> str:
        """Finds a repository name that is free in both the database and on GitHub."""
        candidate_name = base_name
        counter = 1

        while True:
            # 1. Validate database check
            db_repo = await RepositoryService.get_repository_by_name(db, user.id, candidate_name)
            if db_repo is None:
                # 2. Validate GitHub API check
                exists_on_github = await GitHubRepositoryService.check_github_repository_exists(user, candidate_name)
                if not exists_on_github:
                    return candidate_name

            counter += 1
            candidate_name = f"{base_name}-{counter}"

    @staticmethod
    async def create_github_repository(
        user: User,
        repo_name: str,
        is_private: bool
    ) -> dict:
        """Creates a new repository on GitHub under the authenticated user account."""
        if not user.github_access_token_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User GitHub credentials are missing. Please log in again."
            )

        token = decrypt_token(user.github_access_token_encrypted)
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "CodeSync-Backend"
        }
        data = {
            "name": repo_name,
            "private": is_private,
            "auto_init": True,
            "description": "Coding challenge solutions synchronized automatically by CodeSync extension."
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=data)

            if response.status_code == 403:
                logger.error("GitHub API returned rate limit or permissions error.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="GitHub API authorization failed or rate limits exceeded."
                )

            if response.status_code == 422:
                logger.warning(f"Repository creation failed due to duplicate name on GitHub: {repo_name}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Repository '{repo_name}' already exists on GitHub."
                )

            if response.status_code != 201:
                logger.error(f"GitHub repository creation failed. Status: {response.status_code} - Body: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to create repository on GitHub."
                )

            return response.json()

    @staticmethod
    async def fetch_github_repository_details(user: User, repo_name: str) -> dict:
        """Fetches detailed metadata of a GitHub repository."""
        if not user.github_access_token_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User GitHub credentials are missing. Please log in again."
            )

        token = decrypt_token(user.github_access_token_encrypted)
        owner = user.github_username
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "CodeSync-Backend"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(f"Failed to fetch GitHub repository details. Status: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to retrieve repository details from GitHub: {repo_name}"
                )

            return response.json()
