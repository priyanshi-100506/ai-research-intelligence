import os
import sys
import httpx
import asyncio
import logging
import resend
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import insert

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

TECH_DOMAINS = ["Large Language Models", "System Design Architecture", "Cloud Infrastructure"]
MY_INBOX = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com")

db_url = os.getenv("DATABASE_URL")
resend_key = os.getenv("RESEND_API_KEY")
currents_key = os.getenv("NEWS_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not all([db_url, resend_key, currents_key, gemini_key]):
    logging.error("❌ Production Context Secrets Missing!")
    sys.exit(1)

Base = declarative_base()

class ScrapedArticle(Base):
    __tablename__ = 'scraped_articles'
    id = Column(Integer, primary_key=True)
    source_id = Column(String, nullable=False)
    article_id = Column(String, unique=True)
    title = Column(String)
    url = Column(String)
    raw_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Pydantic Analytical Structuring Schema ---
class CuratedArticleSchema(BaseModel):
    title: str = Field(description="The formal clean title of the engineering break")
    summary: str = Field(description="A highly technical, detailed 2-3 sentence distillation explaining the implementation, engine, or structural breakthrough.")
    impact_score: int = Field(description="An engineering impact score from 1 to 10 based on depth, architecture innovation, or foundational relevance.")
    justification: str = Field(description="A single clear sentence explaining exactly why this matters to a senior software engineer.")

async def fetch_realtime_news(client, keyword, api_key):
    url = "https://api.currentsapi.services/v1/search"
    params = {"keywords": keyword, "language": "en", "apiKey": api_key}
    try:
        res = await client.get(url, params=params)
        if res.status_code == 200:
            return res.json().get("news", [])
    except Exception as e:
        logging.error(f"Error scraping {keyword}: {e}")
    return []

def analyze_with_gemini(title: str, snippet: str, client: genai.Client) -> Optional[CuratedArticleSchema]:
    prompt = f"""
    You are an expert Principal Software Architect. Analyze this technical news breaking drop.
    Distill it into a high-density structural summary for a senior developer.
    
    Article Title: {title}
    Raw Snippet Context: {snippet}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CuratedArticleSchema,
                temperature=0.2
            ),
        )
        return CuratedArticleSchema.model_validate_json(response.text)
    except Exception as e:
        logging.error(f"Gemini Curation Failed: {e}")
        return None

async def main():
    logging.info("Checking Currents real-time wire streams...")
    engine = create_engine(db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    
    ai_client = genai.Client(api_key=gemini_key)
    
    all_articles = []
    async with httpx.AsyncClient() as client:
        tasks = [fetch_realtime_news(client, kw, currents_key) for kw in TECH_DOMAINS]
        results = await asyncio.gather(*tasks)
        for batch in results:
            if batch: all_articles.extend(batch)

    new_article_deltas = []
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    seen_urls = set()

    for art in all_articles:
        uid = art.get("url")
        if not uid or uid in seen_urls: continue
        seen_urls.add(uid)
        
        stmt = insert(ScrapedArticle).values(
            source_id="CurrentsAPI",
            article_id=uid,
            title=art.get("title", "Architecture Alert"),
            url=uid,
            raw_content=art.get("description", ""),
            created_at=current_time
        )
        upsert_stmt = stmt.on_conflict_do_nothing(index_elements=['article_id'])
        
        try:
            res = session.execute(upsert_stmt)
            session.commit()
            if res.rowcount > 0:
                # Brand new record found! Send to Gemini for curation instantly
                curation = analyze_with_gemini(art.get("title", ""), art.get("description", ""), ai_client)
                if curation and curation.impact_score >= 6: # High-Signal Threshold Filter
                    new_article_deltas.append((art, curation))
        except Exception as err:
            session.rollback()
            continue

    logging.info(f"📊 Delta Check: Identified {len(new_article_deltas)} high-signal curated items.")

    if new_article_deltas:
        logging.info("🚀 Pushing polished notification drop...")
        resend.api_key = resend_key
        
        html_cards = ""
        for raw, clean in new_article_deltas[:3]:
            html_cards += f"""
            <div style="margin-bottom: 24px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="display: inline-block; background: #e0e7ff; color: #4f46e5; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 4px 10px; border-radius: 20px; margin-bottom: 12px;">
                    ⚡ Impact Score: {clean.impact_score}/10
                </div>
                <h3 style="margin: 0 0 12px 0; font-size: 18px; color: #0f172a; font-weight: 700; line-height: 1.4;">
                    <a href="{raw.get('url')}" style="color: #0f172a; text-decoration: none; border-bottom: 2px solid transparent;" onmouseover="this.style.borderBottom='2px solid #4f46e5'">{clean.title}</a>
                </h3>
                <p style="color: #334155; font-size: 14px; line-height: 1.6; margin: 0 0 16px 0; font-weight: 400;">
                    {clean.summary}
                </p>
                <div style="background: #f8fafc; border-left: 4px solid #94a3b8; padding: 12px 16px; border-radius: 4px;">
                    <span style="color: #475569; font-size: 13px; font-style: italic;"><b>Context:</b> {clean.justification}</span>
                </div>
            </div>
            """
            
        full_polished_email = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; padding: 40px 20px; margin: 0; -webkit-font-smoothing: antialiased;">
            <div style="max-width: 640px; margin: 0 auto;">
                <!-- Header Component -->
                <div style="margin-bottom: 32px; text-align: center;">
                    <h1 style="color: #0f172a; font-size: 26px; font-weight: 800; letter-spacing: -0.025em; margin: 0 0 6px 0;">⚡ Technical News Drop</h1>
                    <p style="color: #64748b; font-size: 14px; margin: 0;">Automated Real-Time Architectural Ingestion Engine</p>
                </div>
                
                <!-- Content Cards Dynamic Stream -->
                {html_cards}
                
                <!-- Footer Component -->
                <div style="text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #94a3b8; font-size: 11px; margin: 0; letter-spacing: 0.025em; text-transform: uppercase;">
                        Event-Driven Processing Grid • Synced via Neon Cluster
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": MY_INBOX,
                "subject": f"⚡ Tech Drop: {len(new_article_deltas)} New Architectural Signals",
                "html": full_polished_email
            })
            logging.info("🎉 Premium structured alert email successfully transmitted!")
        except Exception as m_err:
            logging.error(f"Mailer delivery failed: {m_err}")
    else:
        logging.info("💤 Zero high-signal breaking changes identified this pass.")

    session.close()

if __name__ == "__main__":
    asyncio.run(main())
