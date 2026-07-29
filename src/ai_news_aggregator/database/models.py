from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from src.ai_news_aggregator.core.config import settings

Base = declarative_base()

class ScrapedArticle(Base):
    __tablename__ = 'scraped_articles'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(String, unique=True, nullable=False, index=True)
    source_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    raw_content = Column(Text)
    published_at = Column(DateTime(timezone=True), nullable=False)

class CuratedArticle(Base):
    __tablename__ = 'curated_articles'
    
    id = Column(Integer, primary_key=True)
    scraped_article_id = Column(Integer, ForeignKey('scraped_articles.id', ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    justification = Column(Text, nullable=False)
    tech_stack = Column(String, nullable=False)
    impact_score = Column(Float, nullable=False)
    category = Column(String, default="General")

# Determine if we are running locally/Docker or targeting managed cloud Postgres
is_local_db = any(host in settings.DATABASE_URL for host in ("localhost", "127.0.0.1", "db:5432"))

# SSL is only required for managed cloud hosts (Neon, Supabase, Render, etc.)
connect_args = {} if is_local_db else {"ssl": "require"}

# Engine configuration optimized for stability
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,       # Verifies connection health before each use
    pool_recycle=3600,        # Prevents stale connections by recycling hourly
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)