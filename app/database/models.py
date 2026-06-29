from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.config import settings

# 1. Initialize the Base FIRST so both models can inherit from it safely
Base = declarative_base()

# 2. Raw Staging Table
class ScrapedArticle(Base):
    __tablename__ = "scraped_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False)
    article_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(Text, nullable=False)
    raw_content = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# 3. Refined Curation Table
class CuratedArticle(Base):
    __tablename__ = "curated_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_article_id = Column(Integer, ForeignKey("scraped_articles.id"), unique=True, nullable=False)
    
    summary = Column(Text, nullable=False)
    tech_stack = Column(Text, nullable=False) 
    impact_score = Column(Integer, nullable=False)
    justification = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scraped_article = relationship("ScrapedArticle", backref="curated_data")

# 4. Connection Engines
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes tables inside PostgreSQL if they don't exist yet."""
    Base.metadata.create_all(bind=engine)