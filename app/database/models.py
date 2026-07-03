from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
import os

Base = declarative_base()

class ScrapedArticle(Base):
    __tablename__ = 'scraped_articles'
    id = Column(Integer, primary_key=True)
    article_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    raw_content = Column(Text)
    published_at = Column(DateTime, nullable=False)

def init_db(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
