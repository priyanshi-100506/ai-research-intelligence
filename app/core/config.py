from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# Load .env file explicitly
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    RESEND_API_KEY: str
    NEWS_API_KEY: str
    RECIPIENT_EMAIL: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()