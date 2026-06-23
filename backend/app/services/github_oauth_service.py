import logging
from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger("codesync.services.github_oauth")


class GitHubOAuthService:
    """Asynchronous client service handling GitHub OAuth handshakes and profile discovery."""

    @staticmethod
    def get_authorization_url(state: str) -> str:
        """Generates the GitHub authorization URL for starting OAuth sequence."""
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "scope": "read:user user:email",
            "state": state
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    @staticmethod
    async def exchange_code_for_token(code: str) -> str:
        """Exchanges authorization code for GitHub access token."""
        url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code != 200:
                logger.error(f"GitHub token exchange returned status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to authenticate with GitHub OAuth provider."
                )

            res_data = response.json()
            if "error" in res_data:
                logger.error(f"GitHub token exchange response error: {res_data['error']} - {res_data.get('error_description')}")
                raise ValueError(res_data.get("error_description", res_data["error"]))

            access_token = res_data.get("access_token")
            if not access_token:
                logger.error("No access token found in GitHub response.")
                raise ValueError("Access token not returned by GitHub.")

            return access_token

    @staticmethod
    async def fetch_github_profile(access_token: str) -> dict:
        """Queries the GitHub user API to retrieve profile metadata."""
        url = "https://api.github.com/user"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": "CodeSync-Backend"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to fetch GitHub profile. Status: {response.status_code} - Response: {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to retrieve profile data from GitHub."
                )
            return response.json()

    @staticmethod
    async def fetch_github_primary_email(access_token: str) -> str | None:
        """Fallback helper to fetch verified primary email if profile email is hidden."""
        url = "https://api.github.com/user/emails"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": "CodeSync-Backend"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch email list from GitHub. Status: {response.status_code}")
                return None

            emails = response.json()
            # Search for verified primary email address
            for email_entry in emails:
                if email_entry.get("primary") and email_entry.get("verified"):
                    return email_entry.get("email")

            # Fallback to first primary email if verified flag is missing
            for email_entry in emails:
                if email_entry.get("primary"):
                    return email_entry.get("email")

            return None
