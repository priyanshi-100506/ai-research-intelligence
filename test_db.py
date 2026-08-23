import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Explicitly load from the path
env_path = r"C:\Users\USER\Documents\ai-news-aggregator\.env"
load_dotenv(dotenv_path=env_path)

import pytest

@pytest.mark.asyncio
async def test_connection():
    db_url = os.getenv("DATABASE_URL")
    print(f"DEBUG: Found DATABASE_URL: {db_url}")
    
    engine = None  # Initialize engine to None
    try:
        if not db_url:
            print("ERROR: DATABASE_URL not found!")
            return

        engine = create_async_engine(db_url, connect_args={"ssl": "require"})
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"SUCCESS! Database returned: {result.scalar()}")
    except Exception as e:
        print(f"FAILURE! Connection error: {e}")
    finally:
        if engine:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())