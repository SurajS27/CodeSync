from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App General Settings
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str

    # Database Settings
    DATABASE_URL: str

    # GitHub OAuth Placeholders (for Phase 2)
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # Chrome Extension Settings
    CHROME_EXTENSION_ID: str = ""

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v


# Global Settings Instance
settings = Settings()
