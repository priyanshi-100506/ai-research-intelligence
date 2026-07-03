from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    RESEND_API_KEY: str
    NEWS_API_KEY: str
    RECIPIENT_EMAIL: str

    model_config = SettingsConfigDict(
        env_file=r'C:\Users\USER\Documents\ai-news-aggregator\.env',
        extra='ignore'
    )

settings = Settings()
