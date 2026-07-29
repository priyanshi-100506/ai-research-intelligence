import os
from sqlalchemy.ext.asyncio import create_async_engine

# If the file 'USE_LOCAL_DB' exists, use SQLite, otherwise use Neon
if os.path.exists("USE_LOCAL_DB"):
    db_url = "sqlite:///./local_test.db"
else:
    db_url = os.getenv("DATABASE_URL")

engine = create_async_engine(db_url)