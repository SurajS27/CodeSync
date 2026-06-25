import base64
import logging

import httpx
from fastapi import HTTPException, status

from app.models.user import User
from app.utils.encryption import decrypt_token

logger = logging.getLogger("codesync.services.github_content")


class GitHubContentService:
    """Asynchronous client service interfacing with GitHub API to manage repository file contents."""

    @staticmethod
    async def get_file_metadata(
        user: User, repo_full_name: str, path: str
    ) -> dict | None:
        """Retrieves metadata properties of a file or folder at a specific path on GitHub."""
        if not user.github_access_token_encrypted:
            return None

        token = decrypt_token(user.github_access_token_encrypted)
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "CodeSync-Backend",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 404:
                return None
            logger.warning(
                f"GitHub contents check returned status {response.status_code} for path: {path}"
            )
            return None

    @staticmethod
    async def check_file_exists(
        user: User, repo_full_name: str, path: str
    ) -> str | None:
        """Returns the file's SHA string if the file exists on GitHub, else None."""
        metadata = await GitHubContentService.get_file_metadata(
            user, repo_full_name, path
        )
        if metadata and isinstance(metadata, dict) and "sha" in metadata:
            return metadata["sha"]
        return None

    @staticmethod
    async def create_or_update_file(
        user: User,
        repo_full_name: str,
        path: str,
        content: str,
        commit_message: str,
        sha: str | None = None,
    ) -> dict:
        """Writes or updates a file (based on SHA presence) on GitHub using Base64 encoding."""
        if not user.github_access_token_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User GitHub credentials are missing. Please log in again.",
            )

        token = decrypt_token(user.github_access_token_encrypted)

        # Base64 encode file contents
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "CodeSync-Backend",
        }
        data = {"message": commit_message, "content": encoded_content}
        if sha:
            data["sha"] = sha

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(url, headers=headers, json=data)

            if response.status_code == 403:
                logger.error(
                    "GitHub API returned rate limits or permissions block on content write."
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="GitHub API permission failed or rate limits exceeded on file write.",
                )

            if response.status_code not in (200, 201):
                logger.error(
                    f"Failed to write file. Status: {response.status_code} - Body: {response.text}"
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to write file '{path}' to GitHub repository.",
                )

            return response.json()
