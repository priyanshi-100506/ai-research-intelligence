import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Build the path to .env based on the location of this file (config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Force load the .env file
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    RESEND_API_KEY: str
    NEWS_API_KEY: str
    RECIPIENT_EMAIL: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()