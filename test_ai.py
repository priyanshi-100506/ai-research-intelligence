from app.services.curator_service import AICuratorService

def test_agent():
    print("Spinnin up the AI Curation agent infrastructure...")
    curator = AICuratorService()
    
    mock_title = "Building a localized RAG system with Llama 3 and ChromaDB"
    mock_content = """
    In this guide, Matthew Berman walks through configuring an operational retrieval-augmented generation pipeline.
    We deploy Llama 3 locally using Ollama runtime loops. Data is vectorized using HuggingFace bge-large-en embeddings,
    and stored inside a ChromaDB vector instance database store. The implementation yields a massive 40% latency reduction 
    compared to traditional cloud execution engines, drastically reducing production compute costs.
    """
    
    print("Passing mock telemetry payloads to Gemini 2.5 Flash...")
    analysis = curator.analyze_content(mock_title, mock_content)
    
    print("\n=== AI Curation Engine Analysis Response ===")
    print(f"Summary:\n{analysis.summary}")
    print(f"Tech Stack Extracted: {analysis.tech_stack}")
    print(f"Impact Score: {analysis.impact_score}/10")
    print(f"Justification: {analysis.justification}")

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.getcwd())
    test_agent()
    