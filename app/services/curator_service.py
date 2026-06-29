from google import genai
from google.genai import types
from app.config import settings
from app.services.curator_schema import CuratedArticleAnalysis

class AICuratorService:
    def __init__(self):
        """Initializes the unified Google Gen AI client wrapper using our environment keys."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("CRITICAL: GEMINI_API_KEY is missing from your .env configuration file!")
        
        # Modern 2026 unified SDK initialization mapping
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # We leverage the fast, large-context gemini-2.5-flash for analyzing heavy transcripts
        self.model_name = "gemini-2.5-flash"

    def analyze_content(self, title: str, raw_content: str) -> CuratedArticleAnalysis:
        """
        Passes unstructured source files to Gemini and enforces a strict
        Pydantic data contract output format.
        """
        if not raw_content or len(raw_content.strip()) < 50:
            return CuratedArticleAnalysis(
                summary="Insufficient content available to generate a valid extraction analysis report.",
                tech_stack=[],
                impact_score=1,
                justification="Content too short or missing structural layout."
            )

        prompt = f"""
        You are an elite AI developer and technical product manager curating an industry newsletter.
        Analyze the following raw article/transcript content and extract clear structural insights.

        Source Title: {title}
        Raw Content Streams:
        {raw_content}
        """

        try:
            # Execute structured output loop matching modern SDK parameters
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CuratedArticleAnalysis,
                    temperature=0.2, # Lower temperature forces highly accurate, analytical focus
                ),
            )
            
            # The SDK automatically parses the JSON text directly into our Pydantic schema model object
            return response.parsed
        except Exception as e:
            print(f" -> AI Processing Exception dropped for '{title[:30]}': {str(e)}")
            # Fallback fail-safe mechanism if the LLM validation fails
            return CuratedArticleAnalysis(
                summary=f"Failed to generate automated synthesis due to execution drop error.",
                tech_stack=[],
                impact_score=1,
                justification=f"Error log signature: {str(e)[:100]}"
            )