from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ai_news_aggregator.core.config import settings

# Create the engine
engine = create_engine(settings.DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()