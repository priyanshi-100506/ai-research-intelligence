from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

Base = declarative_base()

class ScrapedArticle(Base):
    __tablename__ = 'scraped_articles'
    id = Column(Integer, primary_key=True)
    article_id = Column(String, unique=True, nullable=False)
    source_id = Column(String, nullable=False)  # Added this missing column
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    raw_content = Column(Text)
    published_at = Column(DateTime, nullable=False)

class CuratedArticle(Base):
    __tablename__ = 'curated_articles'
    id = Column(Integer, primary_key=True)
    scraped_article_id = Column(Integer, ForeignKey('scraped_articles.id'), nullable=False)
    summary = Column(Text, nullable=False)
    justification = Column(Text, nullable=False)
    tech_stack = Column(String, nullable=False)
    impact_score = Column(Float, nullable=False)

# Database Session Factory
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
