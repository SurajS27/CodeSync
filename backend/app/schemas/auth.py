import uuid

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class GitHubLoginResponse(BaseModel):
    """Schema returning the constructed GitHub authorization redirect target and security state."""

    authorization_url: str = Field(
        ..., description="Target GitHub OAuth redirection URL"
    )
    state: str = Field(..., description="Transient anti-forgery state token")


class TokenPayload(BaseModel):
    """Schema representing JWT payload fields."""

    sub: uuid.UUID = Field(..., description="Canonical database user UUID")
    github_id: str = Field(..., description="GitHub unique user account ID")
    exp: int = Field(..., description="Expiration epoch timestamp")


class AuthenticatedUserResponse(BaseModel):
    """Schema returned after a successful OAuth token exchange callback."""

    access_token: str = Field(..., description="FastAPI app JWT access token")
    token_type: str = Field("bearer", description="Access token verification scheme")
    user: UserResponse = Field(
        ..., description="Profile information for the authenticated User"
    )
