import asyncio
import httpx
from sqlalchemy import create_engine
from app.core.logger import get_logger
from app.core.config import settings
from app.core.models import Base, Article
from app.scrapers.currents import CurrentsProvider
from app.services.storage import StorageService
# ADD THIS IMPORT:
from app.services.email_service import send_email_report 

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
    articles = [Article(article_id=a['id'], title=a['title'], url=a['url']) for a in flat_list]
    
    if articles:
        storage.save_articles(articles)
        logger.info(f"Pipeline processed {len(articles)} articles with database-level deduplication.")
        
        # --- ADD THIS CALL ---
        try:
            send_email_report(articles)
            logger.info("Report dispatched successfully.")
        except Exception as e:
            logger.error(f"Failed to dispatch report: {e}")
        # ---------------------
    else:
        logger.info("No articles retrieved.")

if __name__ == '__main__':
    asyncio.run(run_pipeline())