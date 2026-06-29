import os

class Settings:
    # Points directly to the healthy local PostgreSQL container we verified earlier
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/ai_news"
    )

settings = Settings()