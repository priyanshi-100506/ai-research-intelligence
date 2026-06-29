import os
from dotenv import load_dotenv

# Load environment variables from the .env file explicitly
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/ai_news"
    )
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()