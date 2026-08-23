import pytest
import asyncio
from src.ai_news_aggregator.services.curation_service import CurationService

@pytest.mark.asyncio
async def test_agent():
    print("Spinnin up the AI Curation agent infrastructure...")
    curator = CurationService()
    
    mock_title = "Building a localized RAG system with Llama 3 and ChromaDB"
    mock_content = """
    In this guide, Matthew Berman walks through configuring an operational retrieval-augmented generation pipeline.
    We deploy Llama 3 locally using Ollama runtime loops. Data is vectorized using HuggingFace bge-large-en embeddings,
    and stored inside a ChromaDB vector instance database store. The implementation yields a massive 40% latency reduction 
    compared to traditional cloud execution engines, drastically reducing production compute costs.
    """
    
    print("Passing mock telemetry payloads to Gemini...")
    analysis = await asyncio.to_thread(curator.curate, mock_content)
    
    print("\n=== AI Curation Engine Analysis Response ===")
    print(f"Summary:\n{analysis.summary}")
    print(f"Tech Stack Extracted: {analysis.tech_stack}")
    print(f"Impact Score: {analysis.impact_score}/10")
    print(f"Justification: {analysis.justification}")

if __name__ == "__main__":
    asyncio.run(test_agent())

    