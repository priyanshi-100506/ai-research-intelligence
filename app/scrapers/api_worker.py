import os
import httpx
import logging
from datetime import datetime
from typing import List
from pydantic import BaseModel

class ScrapedItemSchema(BaseModel):
    source_id: str
    article_id: str
    title: str
    url: str
    raw_content: str
    published_at: datetime

class ApiIngestionWorker:
    def __init__(self):
        # Safely checks environment tokens
        self.api_key = os.getenv("NEWS_API_KEY", "YOUR_FREE_NEWSAPI_ORG_KEY")
        self.endpoint = "https://newsapi.org/v2/everything"

    async def query_keyword_stream_async(self, client: httpx.AsyncClient, keyword: str, limit: int = 3) -> List[ScrapedItemSchema]:
        logging.info(f"Firing non-blocking API pipeline task for domain keyword: [{keyword}]")
        
        query_params = {
            "q": keyword,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": limit,
            "apiKey": self.api_key
        }
        
        extracted_records = []
        try:
            response = await client.get(self.endpoint, params=query_params, timeout=12.0)
            if response.status_code != 200:
                logging.error(f"NewsAPI error response [{response.status_code}] for keyword: {keyword}")
                return extracted_records
                
            payload = response.json()
            for item in payload.get("articles", []):
                pub_date_str = item.get("publishedAt")
                pub_date = datetime.strptime(pub_date_str[:19], "%Y-%m-%dT%H:%M:%S") if pub_date_str else datetime.utcnow()

                # CRITICAL FIX: Ensure full content text snippet is targeted so Gemini has material to read
                content_payload = item.get("description", "") or item.get("content", "")
                if not content_payload or len(content_payload.strip()) < 10:
                    content_payload = f"Engineering development details tracking keyword update for {keyword}."

                extracted_records.append(ScrapedItemSchema(
                    source_id=keyword, # Used contextually as our Category Header
                    article_id=item.get("url"),
                    title=item.get("title", "Breaking Technology Update"),
                    url=item.get("url", ""),
                    raw_content=content_payload,
                    published_at=pub_date
                ))
        except Exception as api_err:
            logging.error(f"Asynchronous streaming pass failed for network task [{keyword}]: {str(api_err)}")
            
        return extracted_records
