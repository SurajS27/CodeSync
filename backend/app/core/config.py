from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App General Settings
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str

    # Database Settings
    DATABASE_URL: str

    # GitHub OAuth Settings
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str

    # Cryptography & JWT Settings
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENCRYPTION_KEY: str
    OAUTH_STATE_EXPIRE_MINUTES: int = 10

    # Extension Redirection Target
    FRONTEND_URL: str

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        # Avoid validation of the placeholder string if not in production to allow running basic command-lines
        if "placeholder" in v.lower():
            return v
        try:
            from cryptography.fernet import Fernet

            # Test key validity by initializing Fernet
            Fernet(v.encode())
        except Exception as e:
            raise ValueError(f"ENCRYPTION_KEY is not a valid Fernet key: {str(e)}")
        return v

    @model_validator(mode="after")
    def validate_production_keys(self) -> Self:
        if self.ENV.lower() == "production":
            required_keys = {
                "SECRET_KEY": self.SECRET_KEY,
                "ENCRYPTION_KEY": self.ENCRYPTION_KEY,
                "GITHUB_CLIENT_ID": self.GITHUB_CLIENT_ID,
                "GITHUB_CLIENT_SECRET": self.GITHUB_CLIENT_SECRET,
            }
            for key, val in required_keys.items():
                if not val or any(
                    x in val.lower() for x in ["placeholder", "your_", "mock_", "dev_"]
                ):
                    raise ValueError(
                        f"In production mode, {key} must be set to a valid secure key (cannot be empty or placeholder)."
                    )
        return self


# Global Settings Instance
settings = Settings()
