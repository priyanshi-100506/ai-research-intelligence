from pydantic import BaseModel, Field
from google.genai import Client
from google.genai.errors import ClientError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from src.ai_news_aggregator.core.config import settings

class ArticleSummary(BaseModel):
    summary: str = Field(description="A concise summary of the research paper.")
    impact_score: float = Field(description="Impact score between 1 and 10.")
    tech_stack: str = Field(description="Comma separated list of technologies/methods.")
    justification: str = Field(description="Why this paper matters for AI news.")
    category: str = Field(description="Category must be one of: 'Robotics', 'NLP', 'Vision'.")
class CurationService:
    # Update constructor to accept model_name
    def __init__(self, model_name: str = "gemini-3.1-flash-lite"):
        self.client = Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(ClientError)
    )
    def curate(self, raw_content: str) -> ArticleSummary:
        # Use self.model_name dynamically
        prompt = f"""
        Analyze this research paper: {raw_content}
        
        Categorize this paper strictly into one of these three categories: 
        'Robotics', 'NLP', or 'Vision'. 
        If it doesn't fit perfectly, choose the most relevant one.
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ArticleSummary,
            },
        )
        return ArticleSummary.model_validate_json(response.text)