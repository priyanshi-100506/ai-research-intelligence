import arxiv
from ai_news_aggregator.database.models import ScrapedArticle

class ArXivScraper:
    def __init__(self):
        self.client = arxiv.Client(delay_seconds=3.0)

    def fetch_papers(self, query="cat:cs.AI", max_results=5):
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        scraped_data = []
        for result in self.client.results(search):
            article = ScrapedArticle(
                article_id=result.entry_id,
                source_id="arxiv",
                title=result.title,
                url=result.entry_id,
                raw_content=result.summary,
                published_at=result.published
            )
            scraped_data.append(article)
        return scraped_data