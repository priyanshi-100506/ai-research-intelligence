import arxiv
from ai_news_aggregator.database.models import ScrapedArticle

class ArXivScraper:
    def __init__(self):
        self.client = arxiv.Client(delay_seconds=3.0)

    def fetch_papers(self, query="cat:cs.AI", max_results=20) -> list[ScrapedArticle]:
        """
        Fetches latest papers from ArXiv based on query and max_results.
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        scraped_data = []
        for result in self.client.results(search):
            # Extract clean ID from entry_id URL (e.g., 'http://arxiv.org/abs/2401.12345v1' -> '2401.12345v1')
            clean_id = result.entry_id.split("/")[-1]

            article = ScrapedArticle(
                article_id=clean_id,
                source_id="arxiv",
                title=result.title.replace("\n", " ").strip(),
                url=result.entry_id,
                raw_content=result.summary.strip(),
                published_at=result.published
            )
            scraped_data.append(article)
            
        return scraped_data