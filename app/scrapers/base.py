from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

class BaseProvider(ABC):
    @abstractmethod
    async def fetch(self, client, keyword):
        pass

@dataclass
class ArticleMetadata:
    article_id: str
    source_id: str
    title: str
    url: str
    published_at: datetime
    raw_content: str = None
