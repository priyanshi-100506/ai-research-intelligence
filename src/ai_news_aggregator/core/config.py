from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    RESEND_API_KEY: str
    NEWS_API_KEY: str
    RECIPIENT_EMAIL: str
    
    # This allows Pydantic to ignore any extra keys in .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"  # This is the key change!
    )

settings = Settings()