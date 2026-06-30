import sys
import os
# Structural dynamic path guard mapping
sys.path.append(os.getcwd())

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database.models import SessionLocal, CuratedArticle, ScrapedArticle

app = FastAPI(
    title="AI News Aggregator & Curation API",
    description="Production-ready backend engine serving deduplicated, high-impact AI insights.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Session Context Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Strict Pydantic Data Contracts ---
class ArticleDisplaySchema(BaseModel):
    id: int
    title: str
    url: str
    source_id: str
    summary: str
    tech_stack: str
    impact_score: int
    justification: str
    published_at: datetime

    class Config:
        from_attributes = True

# --- API Endpoints ---

@app.get("/", tags=["Root"])
def read_root():
    return {
        "status": "online",
        "message": "AI News Aggregator Core Engine Running",
        "endpoints": ["/api/articles", "/api/articles/high-impact"]
    }

@app.get("/api/articles", response_model=List[ArticleDisplaySchema], tags=["Articles"])
def get_all_articles(
    min_score: int = Query(default=1, ge=1, le=10, description="Filter items by a minimum impact score"),
    limit: int = Query(default=20, ge=1, le=100, description="Limit total returned records"),
    db: Session = Depends(get_db)
):
    """
    Fetches curated news records from the database, joined directly with their raw metadata source fields.
    """
    try:
        # Explicitly query the objects and enforce an inner join relationship
        results = db.query(CuratedArticle).join(
            ScrapedArticle, CuratedArticle.scraped_article_id == ScrapedArticle.id
        ).filter(
            CuratedArticle.impact_score >= min_score
        ).order_by(
            CuratedArticle.impact_score.desc(),
            ScrapedArticle.published_at.desc()
        ).limit(limit).all()

        output = []
        for c in results:
            # Fallback values prevent Pydantic formatting crashes if fields contain empty telemetry strings
            output.append(ArticleDisplaySchema(
                id=int(c.id),
                title=str(c.scraped_article.title or "Untitled"),
                url=str(c.scraped_article.url or "#"),
                source_id=str(c.scraped_article.source_id or "Unknown"),
                summary=str(c.summary or "No summary available."),
                tech_stack=str(c.tech_stack or "None"),
                impact_score=int(c.impact_score if c.impact_score is not None else 1),
                justification=str(c.justification or "No justification provided."),
                published_at=c.scraped_article.published_at
            ))
        
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database serialization failure: {str(e)}")

@app.get("/api/articles/high-impact", response_model=List[ArticleDisplaySchema], tags=["Articles"])
def get_high_impact_articles(db: Session = Depends(get_db)):
    """
    Shortcut portfolio endpoint: Instantly returns top-tier trends (Impact Score >= 7).
    """
    return get_all_articles(min_score=7, limit=10, db=db)