from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    RESEND_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    RECIPIENT_EMAIL: str = ""

    # Optional secret for protecting the /trigger-pipeline endpoint.
    # Set PIPELINE_SECRET=<your-token> in .env or your deployment env vars.
    # If not set, the endpoint is accessible without a token (dev mode).
    PIPELINE_SECRET: Optional[str] = None

    # Comma-separated list of production frontend origins for CORS
    ALLOWED_ORIGINS: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # silently ignore unknown env vars
    )

settings = Settings()