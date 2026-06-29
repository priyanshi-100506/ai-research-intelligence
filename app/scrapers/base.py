from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleMetadata(BaseModel):
    source_id: str         # e.g., YouTube Channel ID or "openai" / "anthropic"
    article_id: str        # Unique Video ID or Blog URL slug
    title: str
    url: str
    published_at: datetime
    raw_content: Optional[str] = None  # Full video transcript or parsed blog body