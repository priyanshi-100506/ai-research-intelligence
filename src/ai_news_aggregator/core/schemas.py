from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    article_id: str
    title: str
    url: HttpUrl
    raw_content: Optional[str] = None
    published_at: datetime
