from pydantic import BaseModel, Field
from typing import List

class CuratedArticleAnalysis(BaseModel):
    summary: str = Field(description="A concise 3-sentence bulleted summary of the core news or breakthrough.")
    tech_stack: List[str] = Field(description="List of specific technologies, models, libraries, or frameworks mentioned.")
    impact_score: int = Field(description="An importance score from 1 (minor update) to 10 (revolutionary/industry-shifting industry milestone).")
    justification: str = Field(description="A 1-sentence explanation backing up the given impact score.")