from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    article_id = Column(String, primary_key=True)
    title = Column(String)
    url = Column(String)
    published_at = Column(DateTime)
