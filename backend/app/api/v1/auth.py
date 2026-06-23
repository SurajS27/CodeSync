import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.core.security import create_access_token, create_oauth_state
from app.models.user import User
from app.schemas.auth import AuthenticatedUserResponse, GitHubLoginResponse
from app.schemas.user import UserResponse
from app.schemas.user import UserCreate
from app.services.github_oauth_service import GitHubOAuthService
from app.services.oauth_state_service import OAuthStateService
from app.services.user_service import UserService
from app.utils.encryption import encrypt_token

logger = logging.getLogger("codesync.api.auth")
router = APIRouter()


@router.get("/github/login", response_model=GitHubLoginResponse)
async def github_login():
    """Generates the secure authorization target URL and anti-forgery state parameters.

    Returns JSON containing these elements to the Chrome Extension.
    """
    state = create_oauth_state()
    authorization_url = GitHubOAuthService.get_authorization_url(state)
    logger.debug(f"Generated OAuth state parameter: {state}")
    return {
        "authorization_url": authorization_url,
        "state": state
    }


@router.get("/github/callback", response_model=AuthenticatedUserResponse)
async def github_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """Processes the redirect code and state callback from GitHub OAuth provider.

    Exchanges authorization code for GitHub access token, retrieves user data,
    stores credentials in database securely encrypted, and yields an API JWT.
    """
    # 1. Anti-forgery validation
    if not OAuthStateService.validate_state(state):
        logger.warning(f"OAuth state parameter validation failed for state: {state}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSRF validation check failed. OAuth state parameter is invalid or expired."
        )

    # 2. Token exchange with GitHub OAuth
    try:
        github_token = await GitHubOAuthService.exchange_code_for_token(code)
    except ValueError as e:
        logger.error(f"GitHub token exchange logic failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub token exchange returned error details: {str(e)}"
        )
    except Exception as e:
        logger.error(f"GitHub connection failure during token exchange: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to establish connection to GitHub servers."
        )

    # 3. Retrieve user profile
    try:
        profile = await GitHubOAuthService.fetch_github_profile(github_token)
    except Exception as e:
        logger.error(f"GitHub profile retrieval failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch profile details from GitHub API: {str(e)}"
        )

    github_id = str(profile.get("id"))
    github_username = profile.get("login")
    github_email = profile.get("email")
    github_avatar_url = profile.get("avatar_url")

    if not github_id or not github_username:
        logger.error("GitHub profile response is missing unique id or username fields.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GitHub profile response is missing essential identifiers."
        )

    # 4. Fetch email fallback if hidden
    if not github_email:
        logger.info(f"Primary email is null for github user {github_username}, querying secondary list...")
        github_email = await GitHubOAuthService.fetch_github_primary_email(github_token)

    # 5. Encrypt access token before persisting in database
    try:
        encrypted_token = encrypt_token(github_token)
    except Exception as e:
        logger.error(f"Token encryption failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to securely persist user authorization token."
        )

    # 6. Locate or create User database records
    user = await UserService.get_user_by_github_id(db, github_id)
    if not user:
        user_create = UserCreate(
            github_id=github_id,
            github_username=github_username,
            github_email=github_email,
            github_avatar_url=github_avatar_url,
            is_active=True
        )
        user = await UserService.create_user(db, user_create, encrypted_token)
        logger.info(f"Registered new User account: {user.id} - username: {github_username}")
    else:
        # Sync profile information updates and secure token
        user.github_username = github_username
        user.github_email = github_email
        user.github_avatar_url = github_avatar_url
        user.github_access_token_encrypted = encrypted_token
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Updated credentials and profile for existing User: {user.id}")

    # 7. Issue application JWT access token
    jwt_token = create_access_token(user_id=str(user.id), github_id=github_id)

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def auth_me(current_user: User = Depends(get_current_user)):
    """Retrieves profile information for the authenticated User."""
    return current_user


@router.post("/logout")
async def auth_logout(current_user: User = Depends(get_current_user)):
    """Logs out the user.

    Current MVP behavior simply returns success. Token revocation
    or denylist management will be added in a future milestone.
    """
    logger.info(f"User {current_user.id} logged out successfully.")
    return {"message": "Logged out successfully."}
