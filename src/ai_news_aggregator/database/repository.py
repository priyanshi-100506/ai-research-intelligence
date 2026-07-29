# src/ai_news_aggregator/database/repository.py
import logging
from typing import Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.ai_news_aggregator.database.models import ScrapedArticle, CuratedArticle

logger = logging.getLogger(__name__)

class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ✅ FIXED: Added `self` here
    async def get_existing_article_ids(self) -> Set[str]:
        """Fetch set of all existing scraped article IDs for bulk deduplication."""
        result = await self.session.execute(select(ScrapedArticle.article_id))
        return {row[0] for row in result.all()}

    async def save_article_with_curation(
        self, paper: ScrapedArticle, summary_data
    ) -> CuratedArticle:
        """Saves scraped paper and its associated curation atomically in one transaction."""
        self.session.add(paper)
        await self.session.flush()  # Populates paper.id without committing transaction

        curated = CuratedArticle(
            scraped_article_id=paper.id,
            summary=summary_data.summary,
            impact_score=summary_data.impact_score,
            tech_stack=summary_data.tech_stack,
            justification=summary_data.justification,
            category=getattr(summary_data, "category", "General"),
        )
        self.session.add(curated)
        await self.session.commit()
        return curated