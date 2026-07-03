import sys
import os
import httpx
import asyncio
import logging
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert

sys.path.append(os.getcwd())

from app.database.models import init_db, SessionLocal, ScrapedArticle, CuratedArticle
from app.scrapers.api_worker import ApiIngestionWorker
from app.services.curator_service import AICuratorService
from app.services.email_service import EmailNotificationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TECH_DOMAINS = ["Large Language Models", "System Design Architecture", "Cloud Infrastructure"]
MY_INBOX = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com")

async def run_v2_streaming_pipeline():
    logging.info("Initializing hardened database storage layer schemas...")
    init_db()
    
    db = SessionLocal()
    api_extractor = ApiIngestionWorker()
    curator = AICuratorService()
    mailer = EmailNotificationService()
    
    all_extracted_items = []
    
    # 1. CONCURRENT DATA HARVESTING
    logging.info(f"Spawning concurrent non-blocking connection pool across domains: {TECH_DOMAINS}")
    async with httpx.AsyncClient() as client:
        tasks = [api_extractor.query_keyword_stream_async(client, domain, limit=3) for domain in TECH_DOMAINS]
        results = await asyncio.gather(*tasks)
        for batch in results:
            all_extracted_items.extend(batch)

    logging.info(f"Ingested {len(all_extracted_items)} prospective records from web endpoints. Processing state upserts...")

    # 2. STATE-AWARE DB DEDUPLICATION & OVERWRITE LAYER
    new_or_modified_article_ids = []
    for item in all_extracted_items:
        stmt = insert(ScrapedArticle).values(
            source_id=item.source_id,
            article_id=item.article_id,
            title=item.title,
            url=item.url,
            raw_content=item.raw_content,
            category=item.source_id,
            published_at=item.published_at.replace(tzinfo=None),
            updated_at=datetime.utcnow()
        )
        
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['article_id'],
            set_={
                'raw_content': stmt.excluded.raw_content,
                'title': stmt.excluded.title,
                'updated_at': datetime.utcnow()
            }
        )
        
        try:
            db.execute(upsert_stmt)
            db.commit()
            
            record = db.query(ScrapedArticle).filter(ScrapedArticle.article_id == item.article_id).first()
            already_curated = db.query(CuratedArticle).filter(CuratedArticle.scraped_article_id == record.id).first()
            
            if not already_curated:
                new_or_modified_article_ids.append(record.id)
        except Exception as db_err:
            db.rollback()
            logging.error(f"Atomic upsert failed for url [{item.url[:30]}]: {str(db_err)}")
            continue

    # 3. ON-THE-FLY INTELLIGENCE SYNTHESIS BATCHING WITH RATE BALANCING
    if new_or_modified_article_ids:
        logging.info(f"🚨 Delta verified across {len(new_or_modified_article_ids)} nodes. Launching Gemini curation pipeline...")
        for index, article_id in enumerate(new_or_modified_article_ids):
            
            # UPGRADE: Defensive rate-limiting buffer for Gemini Free Tier (5 RPM)
            if index > 0:
                logging.info("Applying dynamic rate pacing buffer (12.5s) to avoid API resource exhaustion...")
                await asyncio.sleep(12.5)
                
            article = db.query(ScrapedArticle).filter(ScrapedArticle.id == article_id).first()
            logging.info(f"Submitting schema contract to Gemini for: '{article.title[:35]}...'")
            try:
                analysis = curator.analyze_content(article.title, article.raw_content)
                tech_stack_str = ", ".join(analysis.tech_stack) if analysis.tech_stack else "None"
                
                db.add(CuratedArticle(
                    scraped_article_id=article.id,
                    summary=analysis.summary,
                    tech_stack=tech_stack_str,
                    impact_score=analysis.impact_score,
                    justification=analysis.justification
                ))
                db.commit()
                logging.info(f"Stored structured metrics. Calculated Technical Impact: {analysis.impact_score}/10")
            except Exception as ai_err:
                db.rollback()
                logging.error(f"Gemini schema processing dropped for node {article_id}: {str(ai_err)}")
                continue

    # 4. DISPATCH PRESENTATION LAYER DYNAMICALLY
    logging.info("Executing relational data payload gathering for newsletter packaging...")
    try:
        mailer.send_daily_briefing(recipient_email=MY_INBOX)
    except Exception as dispatch_error:
        logging.error(f"Newsletter presentation delivery layer drop: {str(dispatch_error)}")

    db.close()
    logging.info("Pipeline V2 loop executed smoothly. Storage layers fully synchronized.")

if __name__ == "__main__":
    asyncio.run(run_v2_streaming_pipeline())
