import os
import sys
import httpx
import asyncio
import logging
import resend
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import insert

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

# Production Keyword Streams
TECH_DOMAINS = ["Large Language Models", "System Design Architecture", "Cloud Infrastructure"]
MY_INBOX = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com")

db_url = os.getenv("DATABASE_URL")
resend_key = os.getenv("RESEND_API_KEY")
currents_key = os.getenv("NEWS_API_KEY") # Reads your fresh real-time token seamlessly

if not all([db_url, resend_key, currents_key]):
    logging.error("❌ Production Secrets Missing in running context environment!")
    sys.exit(1)

Base = declarative_base()

class ScrapedArticle(Base):
    __tablename__ = 'scraped_articles'
    id = Column(Integer, primary_key=True)
    article_id = Column(String, unique=True)
    title = Column(String)
    url = Column(String)
    raw_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

async def fetch_realtime_news(client, keyword, api_key):
    # Switches query structure to hit Currents API's real-time extraction pipeline
    url = "https://api.currentsapi.services/v1/search"
    params = {
        "keywords": keyword,
        "language": "en",
        "apiKey": api_key
    }
    try:
        res = await client.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            return data.get("news", [])
    except Exception as e:
        logging.error(f"Error scraping {keyword} from real-time stream: {e}")
    return []

async def main():
    logging.info("Checking Currents API for live breaking technical deltas...")
    engine = create_engine(db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    Base.metadata.create_all(engine)
    
    all_articles = []
    async with httpx.AsyncClient() as client:
        tasks = [fetch_realtime_news(client, kw, currents_key) for kw in TECH_DOMAINS]
        results = await asyncio.gather(*tasks)
        for batch in results:
            if batch: all_articles.extend(batch)

    new_article_deltas = []
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)

    for art in all_articles:
        uid = art.get("url")
        if not uid: continue
        
        stmt = insert(ScrapedArticle).values(
            article_id=uid,
            title=art.get("title", "Breaking Architecture Alert"),
            url=uid,
            raw_content=art.get("description", "No raw context summary supplied."),
            created_at=current_time
        )
        
        upsert_stmt = stmt.on_conflict_do_nothing(index_elements=['article_id'])
        res = session.execute(upsert_stmt)
        session.commit()
        
        if res.rowcount > 0:
            new_article_deltas.append(art)

    logging.info(f"📊 Real-Time Delta Check: Identified {len(new_article_deltas)} brand new breaking entries.")

    if new_article_deltas:
        logging.info("🚀 New dynamic developments detected! Transmitting instant news drop...")
        resend.api_key = resend_key
        
        html_items = ""
        # Take the top 3 high-signal newly dropped articles to list in the notification email
        for art in new_article_deltas[:3]:
            html_items += f"""
            <div style='margin-bottom: 20px; padding: 15px; background: #f8fafc; border-left: 4px solid #4f46e5; border-radius: 4px;'>
                <h4 style='margin:0 0 5px 0;'><a href='{art.get("url")}' style='color:#1e293b; text-decoration:none; font-weight:bold;'>{art.get("title")}</a></h4>
                <p style='color:#475569; font-size:13px; margin:0;'>{art.get("description")}</p>
            </div>
            """
            
        email_body = f"""
        <html>
            <body style="font-family: sans-serif; color: #1e293b; padding: 20px;">
                <h2 style="color: #4f46e5; margin-top: 0;">⚡ Live Technical News Drop</h2>
                <p style="font-size: 14px; color: #64748b;">The tracking engine identified the following live updates on the wire:</p>
                {html_items}
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;"/>
                <small style="color: #94a3b8;">Event-Driven Processing Grid • Synced to Real-Time Streams</small>
            </body>
        </html>
        """
        
        try:
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": MY_INBOX,
                "subject": f"⚡ Live Technical Drop: {len(new_article_deltas)} New Technical Updates",
                "html": email_body
            })
            logging.info(f"🎉 Alert email successfully sent to {MY_INBOX}!")
        except Exception as m_err:
            logging.error(f"Mailer delivery failed: {m_err}")
    else:
        logging.info("💤 Zero new real-time changes breaking since last check. Exiting branch cleanly.")

    session.close()

if __name__ == "__main__":
    asyncio.run(main())
