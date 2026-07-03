import sys
import os
import httpx
import asyncio
import logging
from datetime import datetime, timezone
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
    logging.info("Initializing schemas on Neon cloud platform...")
    init_db()
    
    db = SessionLocal()
    curator = AICuratorService()
    mailer = EmailNotificationService()
    
    news_key = os.getenv("NEWS_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    resend_key = os.getenv("RESEND_API_KEY")
    
    logging.info(f"🔑 Diagnostic - NEWS_API_KEY: {'FOUND' if news_key else 'MISSING'}")
    logging.info(f"🔑 Diagnostic - GEMINI_API_KEY: {'FOUND' if gemini_key else 'MISSING'}")
    logging.info(f"🔑 Diagnostic - RESEND_API_KEY: {'FOUND' if resend_key else 'MISSING'}")
    
    if not news_key:
        logging.error("❌ Exiting: Missing API structural auth tokens.")
        db.close()
        return

    all_extracted_items = []
    logging.info("Connecting to live streaming API targets...")
    api_extractor = ApiIngestionWorker()
    async with httpx.AsyncClient() as client:
        tasks = [api_extractor.query_keyword_stream_async(client, domain, limit=3) for domain in TECH_DOMAINS]
        results = await asyncio.gather(*tasks)
        for batch in results:
            all_extracted_items.extend(batch)

    new_or_modified_article_ids = []
    current_utc_time = datetime.now(timezone.utc).replace(tzinfo=None)
    
    for item in all_extracted_items:
        stmt = insert(ScrapedArticle).values(
            source_id=item.source_id,
            article_id=item.article_id,
            title=item.title,
            url=item.url,
            raw_content=item.raw_content,
            category=item.source_id,
            published_at=item.published_at.replace(tzinfo=None),
            created_at=current_utc_time,
            updated_at=current_utc_time
        )
        
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['article_id'],
            set_={
                'raw_content': stmt.excluded.raw_content,
                'title': stmt.excluded.title,
                'updated_at': current_utc_time
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
            continue

    logging.info(f"📊 Filter Result: {len(new_or_modified_article_ids)} new elements.")

    if new_or_modified_article_ids and gemini_key:
        for article_id in new_or_modified_article_ids:
            await asyncio.sleep(12)
            article = db.query(ScrapedArticle).filter(ScrapedArticle.id == article_id).first()
            try:
                analysis = curator.analyze_content(article.title, article.raw_content)
                tech_stack_str = ", ".join(analysis.tech_stack) if analysis.tech_stack else "None"
                
                db.add(CuratedArticle(
                    scraped_article_id=article.id,
                    summary=analysis.summary,
                    tech_stack=tech_stack_str,
                    impact_score=analysis.impact_score,
                    justification=analysis.justification,
                    created_at=current_utc_time
                ))
                db.commit()
            except Exception:
                db.rollback()
                continue

    if resend_key:
        try:
            logging.info("Force Triggering Email dispatch function...")
            mailer.send_daily_briefing(recipient_email=MY_INBOX)
        except Exception as err:
            logging.error(f"Mailer call crashed: {err}")

    db.close()
    logging.info("Execution sequence wrapped cleanly.")
