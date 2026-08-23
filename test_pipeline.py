import pytest
import asyncio
from datetime import datetime, timezone
from src.ai_news_aggregator.services.pipeline_service import PipelineService
from src.ai_news_aggregator.database.models import ScrapedArticle

@pytest.mark.asyncio
async def test_pipeline(monkeypatch):
    print('🚀 Testing Pipeline logic with mock data...')
    
    # Create a mock paper to avoid scraping 20 results and doing 20 LLM calls
    mock_paper = ScrapedArticle(
        article_id="mock_test_paper_123",
        source_id="arxiv",
        title="Test Mock Title for RAG Search",
        url="http://arxiv.org/abs/mock_test_paper_123",
        raw_content="This is a test summary of a mock paper about AI and machine learning curation.",
        published_at=datetime.now(timezone.utc)
    )
    
    # Mock the fetch_papers method
    from src.ai_news_aggregator.scrapers.arxiv_scraper import ArXivScraper
    monkeypatch.setattr(ArXivScraper, "fetch_papers", lambda self, *args, **kwargs: [mock_paper])
    
    try:
        service = PipelineService()
        await service.run_pipeline()
        print('✅ Pipeline completed successfully.')
    except Exception as e:
        print(f'❌ Pipeline failed: {e}')
        raise e


if __name__ == '__main__':
    asyncio.run(test_pipeline())
