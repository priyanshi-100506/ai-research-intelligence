import asyncio
import httpx
from datetime import datetime
from app.core.logger import get_logger
from app.core.config import settings
from app.scrapers.currents import CurrentsProvider

# Initialize logger and settings
logger = get_logger('pipeline')

async def run_pipeline():
    KEYWORDS = ['Cloud Infrastructure', 'System Design Architecture', 'Large Language Models', 'AI Agents', 'Cybersecurity', 'Database Scaling']
    
    # Initialize the provider (This is now swappable!)
    provider = CurrentsProvider(settings.NEWS_API_KEY)
    
    async with httpx.AsyncClient() as client:
        # We call the interface, not the API-specific implementation directly
        tasks = [provider.fetch(client, keyword) for keyword in KEYWORDS]
        results = await asyncio.gather(*tasks)
        
    all_articles = [item for sublist in results for item in sublist]
    
    if all_articles:
        logger.info(f"Pipeline complete. Aggregated {len(all_articles)} total articles.")
    else:
        logger.info("Pipeline complete. No new data retrieved.")

if __name__ == '__main__':
    asyncio.run(run_pipeline())
