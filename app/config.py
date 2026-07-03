from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Ensure the .env file is loaded
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    RESEND_API_KEY: str
    NEWS_API_KEY: str
    RECIPIENT_EMAIL: str

    # This maps the environment variables to the class attributes
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

# Initialize settings
settings = Settings()