import secrets
from fastapi import APIRouter, Query, Depends, BackgroundTasks, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

from src.ai_news_aggregator.database.models import AsyncSessionLocal, CuratedArticle, ScrapedArticle
from src.ai_news_aggregator.services.pipeline_service import PipelineService
from src.ai_news_aggregator.config import settings

router = APIRouter(prefix="/api/v1", tags=["API v1"])

# Module-level limiter — mirrors the one in main.py (same key_func)
limiter = Limiter(key_func=get_remote_address)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


def verify_pipeline_secret(x_pipeline_secret: Optional[str] = Header(None)):
    """
    Validates the X-Pipeline-Secret header when PIPELINE_SECRET env var is set.
    In dev mode (PIPELINE_SECRET not configured), all requests pass through.
    """
    expected = settings.PIPELINE_SECRET
    if expected is None:
        return  # dev mode — open access
    if x_pipeline_secret is None or not secrets.compare_digest(x_pipeline_secret, expected):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid X-Pipeline-Secret header.",
        )


@router.get("/articles", summary="List curated research articles")
async def get_articles(
    min_score: float = Query(1.0, ge=0, le=10, description="Minimum impact score (0–10)"),
    category: str = Query(None, description="Filter by research category"),
    db: AsyncSession = Depends(get_db),
):
    """Return curated articles filtered by impact score and category."""
    stmt = (
        select(CuratedArticle, ScrapedArticle)
        .join(ScrapedArticle, CuratedArticle.scraped_article_id == ScrapedArticle.id)
        .filter(CuratedArticle.impact_score >= min_score)
    )
    if category and category.strip() and category.lower() != "all":
        stmt = stmt.filter(CuratedArticle.category == category)

    result = await db.execute(stmt.order_by(ScrapedArticle.id.desc()))
    articles = result.all()

    return [
        {
            "title": s.title,
            "url": s.url,
            "summary": c.summary,
            "justification": c.justification,
            "tech_stack": c.tech_stack,
            "impact_score": c.impact_score,
            "category": c.category,
            "source_id": "ArXiv",
            "published_date": (
                s.published_date.strftime("%Y-%m-%d")
                if hasattr(s, "published_date") and s.published_date
                else "Recent"
            ),
        }
        for c, s in articles
    ]


@router.post(
    "/trigger-pipeline",
    status_code=202,
    summary="Trigger the ingestion pipeline",
    dependencies=[Depends(verify_pipeline_secret)],
)
@limiter.limit("5/minute")
async def trigger_pipeline(
    request: Request,
    background_tasks: BackgroundTasks,
    model: str = Query("gemini-2.5-flash", description="Gemini model for curation"),
):
    """
    Triggers the ArXiv ingestion + Gemini curation pipeline as a background task.

    **Rate limit:** 5 requests / minute per IP address.

    **Auth (when PIPELINE_SECRET is set):** Pass `X-Pipeline-Secret: <your-token>` header.
    """
    pipeline = PipelineService(model_name=model)
    background_tasks.add_task(pipeline.run_pipeline)
    return {"status": "accepted", "message": f"Ingestion pipeline triggered with model: {model}"}