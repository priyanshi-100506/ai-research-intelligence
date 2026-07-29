from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.ai_news_aggregator.database.models import AsyncSessionLocal, CuratedArticle, ScrapedArticle

router = APIRouter(prefix="/api")

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

@router.get("/articles")
async def get_articles(
    min_score: float = Query(1.0), 
    category: str = Query(None), 
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(CuratedArticle, ScrapedArticle)
        .join(ScrapedArticle, CuratedArticle.scraped_article_id == ScrapedArticle.id)
        .filter(CuratedArticle.impact_score >= min_score)
    )
    if category and category.strip():
        stmt = stmt.filter(CuratedArticle.category == category)
    
    result = await db.execute(stmt.order_by(ScrapedArticle.id.desc()))
    articles = result.all()
    
    return [{
        "title": s.title, "url": s.url, "summary": c.summary, 
        "justification": c.justification, "tech_stack": c.tech_stack, 
        "impact_score": c.impact_score, "category": c.category, "source_id": "ArXiv"
    } for c, s in articles]