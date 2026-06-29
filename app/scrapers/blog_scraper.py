import feedparser
from datetime import datetime, timezone
import time
from typing import List
from app.scrapers.base import ArticleMetadata
from html_to_markdown import convert 

class BlogScraper:
    def __init__(self):
        self.feeds = {
            "openai": "https://openai.com/news/rss.xml",
            "anthropic": "https://www.anthropic.com/index.xml"
        }

    def fetch_recent_articles(self, max_age_hours: int = 24) -> List[ArticleMetadata]:
        recent_articles = []
        now = datetime.now(timezone.utc)

        for source_name, feed_url in self.feeds.items():
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                published_parsed = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)
                if not published_parsed:
                    continue

                published_dt = datetime.fromtimestamp(time.mktime(published_parsed), timezone.utc)
                age_hours = (now - published_dt).total_seconds() / 3600

                if age_hours <= max_age_hours:
                    raw_html = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
                    clean_markdown = str(convert(raw_html)) if raw_html else ""

                    recent_articles.append(ArticleMetadata(
                        source_id=source_name,
                        article_id=entry.id if hasattr(entry, 'id') else entry.link,
                        title=entry.title,
                        url=entry.link,
                        published_at=published_dt,
                        raw_content=clean_markdown
                    ))
        return recent_articles