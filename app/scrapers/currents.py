from .base import BaseProvider
import httpx

class CurrentsProvider(BaseProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    async def fetch(self, client, keyword):
        url = 'https://api.currentsapi.services/v1/search'
        params = {'keywords': keyword, 'language': 'en', 'apiKey': self.api_key, 'page_size': 5}
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get('news', [])
