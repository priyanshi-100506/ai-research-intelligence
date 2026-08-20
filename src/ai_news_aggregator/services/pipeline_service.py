import asyncio
import logging
from src.ai_news_aggregator.scrapers.arxiv_scraper import ArXivScraper
from src.ai_news_aggregator.services.curation_service import CurationService
from src.ai_news_aggregator.database.models import AsyncSessionLocal
from src.ai_news_aggregator.database.repository import ArticleRepository
from src.ai_news_aggregator.core.shared import broadcaster

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineService:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name

    async def run_pipeline(self):
        logger.info(f"Pipeline started using model: {self.model_name}")
        scraper = ArXivScraper()
        curator = CurationService(model_name=self.model_name)
        
        async with AsyncSessionLocal() as db:
            repo = ArticleRepository(db)
            try:
                # 1. Fetch candidates from scraper
                all_scraped_papers = await asyncio.to_thread(scraper.fetch_papers)
                logger.info(f"Fetched {len(all_scraped_papers)} candidates from ArXiv")
                
                # 2. Bulk Deduplication using Repository
                existing_ids = await repo.get_existing_article_ids()
                new_papers = [p for p in all_scraped_papers if p.article_id not in existing_ids]
                
                skipped_count = len(all_scraped_papers) - len(new_papers)
                logger.info(f"Deduplication: Skipped {skipped_count} duplicates. Processing {len(new_papers)} new.")
                
                if not new_papers:
                    logger.info("No new papers to process.")
                    return

                # 3. Process each new paper
                for paper in new_papers:
                    # AI Curation with fallback
                    try:
                        summary_data = await asyncio.to_thread(curator.curate, paper.raw_content)
                    except Exception as e:
                        logger.error(f"Curation API call failed for {paper.article_id}: {e}. Using dummy fallback.")
                        summary_data = type("Dummy", (), {
                            "summary": "Summary unavailable due to curation failure.", 
                            "justification": "N/A", 
                            "tech_stack": "N/A", 
                            "impact_score": 0.0, 
                            "category": "General"
                        })()

                    # Save paper + curation atomically via Repository
                    await repo.save_article_with_curation(paper, summary_data)

                    # Helper to safely extract attributes whether summary_data is an object or dict
                    get_val = lambda key, default: getattr(summary_data, key, summary_data.get(key, default) if isinstance(summary_data, dict) else default)

                    # 4. Broadcast live update
                    await broadcaster.broadcast({
                        "title": paper.title,
                        "summary": get_val("summary", "N/A"),
                        "impact_score": get_val("impact_score", 0.0),
                        "tech_stack": get_val("tech_stack", "N/A"),
                        "category": get_val("category", "General"),
                        "justification": get_val("justification", ""),
                        "url": paper.url
                    })
                    
                    logger.info(f"Successfully curated & saved: {paper.title[:30]}...")
                    await asyncio.sleep(1)  # Rate pacing for SSE stream
                        
            except Exception as e:
                logger.error(f"Pipeline execution failed: {e}", exc_info=True)
                await db.rollback()