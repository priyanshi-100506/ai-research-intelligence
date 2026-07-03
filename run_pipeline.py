import asyncio
import httpx
from sqlalchemy import create_engine
from app.core.logger import get_logger
from app.core.config import settings
from app.core.models import Base, Article
from app.scrapers.currents import CurrentsProvider
from app.services.storage import StorageService

logger = get_logger('pipeline')
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)

async def run_pipeline():
    KEYWORDS = ['Cloud Infrastructure', 'System Design Architecture', 'Large Language Models', 'AI Agents', 'Cybersecurity', 'Database Scaling']
    provider = CurrentsProvider(settings.NEWS_API_KEY)
    storage = StorageService(engine)
    
    async with httpx.AsyncClient() as client:
        tasks = [provider.fetch(client, keyword) for keyword in KEYWORDS]
        results = await asyncio.gather(*tasks)
    
    flat_list = [item for sublist in results for item in sublist]
    
    # Prepare Article objects
    articles = [Article(article_id=a['id'], title=a['title'], url=a['url']) for a in flat_list]
    
    if articles:
        storage.save_articles(articles)
        logger.info(f"Pipeline processed {len(articles)} articles with database-level deduplication.")
    else:
        logger.info("No articles retrieved.")

if __name__ == '__main__':
    asyncio.run(run_pipeline())
