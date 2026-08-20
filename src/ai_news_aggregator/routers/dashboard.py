from fastapi import APIRouter, Request, BackgroundTasks, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.ai_news_aggregator.database.models import AsyncSessionLocal, CuratedArticle, ScrapedArticle
from src.ai_news_aggregator.services.pipeline_service import PipelineService

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="src/ai_news_aggregator/templates")

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

@router.get("/")
async def index(
    request: Request, 
    category: str = Query("All"), 
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(CuratedArticle, ScrapedArticle)
        .join(ScrapedArticle, CuratedArticle.scraped_article_id == ScrapedArticle.id)
    )
    if category != "All":
        stmt = stmt.filter(CuratedArticle.category == category)
    stmt = stmt.order_by(CuratedArticle.id.desc())
    
    result = await db.execute(stmt)
    articles = result.all()
    
    # ✅ Fixed TemplateResponse signature using explicit keyword arguments
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "articles": articles, 
            "current_category": category
        }
    )

@router.post("/trigger-pipeline", status_code=202)
async def trigger_pipeline(
    background_tasks: BackgroundTasks, 
    model: str = Query("gemini-2.5-flash")
):
    pipeline = PipelineService(model_name=model)
    background_tasks.add_task(pipeline.run_pipeline)
    return {"status": "success", "message": f"Pipeline started with model: {model}"}