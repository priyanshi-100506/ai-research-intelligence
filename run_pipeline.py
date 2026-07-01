import sys
import os
from datetime import datetime, timedelta
import logging

# Path injection safeguard to guarantee package imports resolve cleanly from anywhere
sys.path.append(os.getcwd())

from app.database.models import init_db, SessionLocal, ScrapedArticle, CuratedArticle
from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.blog_scraper import BlogScraper
from app.services.curator_service import AICuratorService

# Setup structured system logging instead of raw print statements
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# CONFIGURATION BOUNDARY (Moving magic numbers to a centralized settings matrix)
# ==============================================================================
LOOKBACK_HOURS = 24
DEFAULT_MAX_AGE_HOURS = 48
DEFAULT_YT_LIMIT = 2
MY_INBOX = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com") # Pulled from ENV with safe fallback

TARGET_SOURCES = [
    {
        "name": "AWS Architecture",
        "url": "https://aws.amazon.com/blogs/architecture/feed/",
        "category": "Cloud Architecture",
        "parser_type": "rss",
        "max_age_hours": DEFAULT_MAX_AGE_HOURS
    },
    {
        "name": "GitHub Engineering",
        "url": "https://github.blog/category/engineering/feed/",
        "category": "Software Engineering",
        "parser_type": "rss",
        "max_age_hours": DEFAULT_MAX_AGE_HOURS
    },
    {
        "name": "Netflix Tech Blog",
        "url": "https://netflixtechblog.com/feed",
        "category": "Systems Design",
        "parser_type": "rss",
        "max_age_hours": DEFAULT_MAX_AGE_HOURS
    },
    {
        "name": "Matthew Berman",
        "url": "@matthew_berman",
        "category": "AI & Automation",
        "parser_type": "youtube",
        "max_limit": DEFAULT_YT_LIMIT
    }
]

def run_ingestion_pipeline():
    logging.info("Initializing database schemas...")
    init_db()
    
    db = SessionLocal()
    curator = AICuratorService()
    
    new_scraped_entries = 0
    all_items = []
    
    try:
        # Initialize scraper workers
        blog_worker = BlogScraper()
        
        # ======================================================================
        # PHASE 1: GENUINE CONFIG-DRIVEN INGESTION
        # ======================================================================
        logging.info("Processing configured ingestion sources...")
        
        for source in TARGET_SOURCES:
            logging.info(f"Polling Source: {source['name']} | Category: {source['category']}")
            
            try:
                # FIXED: The scraper now explicitly ingests the configuration URL target
                if source["parser_type"] == "rss":
                    articles = blog_worker.fetch_recent_articles(
                        target_url=source["url"], 
                        max_age_hours=source["max_age_hours"]
                    )
                    all_items.extend(articles)
                    logging.info(f" -> Collected {len(articles)} articles from {source['name']}")
                    
                elif source["parser_type"] == "youtube":
                    yt_worker = YouTubeScraper(channel_ids=[source["url"]])
                    videos = yt_worker.fetch_recent_videos(max_limit=source["max_limit"])
                    all_items.extend(videos)
                    logging.info(f" -> Indexed {len(videos)} video listings from channel {source['name']}")
            except Exception as source_err:
                # Defensive isolation: a single broken feed or network failure won't kill the whole run
                logging.error(f"Failed to ingest from source {source['name']}: {str(source_err)}")

        # ======================================================================
        # PHASE 2: BATCHED STORAGE & TRANSCRIPT DEDUPLICATION
        # ======================================================================
        logging.info(f"Processing database deduplication layer for {len(all_items)} aggregate entries...")
        
        pending_scraped_records = []
        
        for item in all_items:
            existing = db.query(ScrapedArticle).filter(ScrapedArticle.article_id == item.article_id).first()
            if existing:
                continue
                
            content_body = item.raw_content
            # Late-bound execution: only load heavy multimedia transcripts if the shell record is unique
            if item.source_id.startswith('@') and not content_body:
                logging.info(f" -> Fetching full audio transcript for video: '{item.title[:40]}...'")
                try:
                    yt_transcript_worker = YouTubeScraper(channel_ids=[item.source_id])
                    content_body = yt_transcript_worker.get_transcript(item.article_id)
                except Exception as trans_err:
                    logging.error(f"Transcript extraction dropped for {item.article_id}: {str(trans_err)}")
                    continue
                
            new_record = ScrapedArticle(
                source_id=item.source_id,
                article_id=item.article_id,
                title=item.title,
                url=item.url,
                raw_content=content_body,
                published_at=item.published_at.replace(tzinfo=None)
            )
            pending_scraped_records.append(new_record)
            
        # FIXED: Moving from slow sequential loop commits to single-transaction batch operations
        if pending_scraped_records:
            try:
                db.add_all(pending_scraped_records)
                db.commit()
                new_scraped_entries = len(pending_scraped_records)
                logging.info(f"Database batch update successful. Saved {new_scraped_entries} net-new rows.")
            except Exception as batch_db_err:
                db.rollback()
                logging.error(f"Database batch storage failure: {str(batch_db_err)}")
        else:
            logging.info("Zero net-new entries detected at database border.")

        # ======================================================================
        # PHASE 3: ISOLATED AI CURATION LOOP
        # ======================================================================
        logging.info("Running AI Curation Processing Engine...")
        uncurated_records = db.query(ScrapedArticle).filter(
            ~ScrapedArticle.id.in_(db.query(CuratedArticle.scraped_article_id))
        ).all()
        
        logging.info(f"Found {len(uncurated_records)} uncurated records awaiting analysis.")
        
        pending_curated_records = []
        
        for article in uncurated_records:
            logging.info(f" -> Invoking Gemini 2.5 Flash validation context for: '{article.title[:40]}...'")
            try:
                analysis = curator.analyze_content(article.title, article.raw_content)
                tech_stack_str = ", ".join(analysis.tech_stack) if analysis.tech_stack else "None"
                
                new_curated = CuratedArticle(
                    scraped_article_id=article.id,
                    summary=analysis.summary,
                    tech_stack=tech_stack_str,
                    impact_score=analysis.impact_score,
                    justification=analysis.justification
                )
                pending_curated_records.append(new_curated)
                logging.info(f"    [Validated Contract] Impact Score: {analysis.impact_score}/10")
            except Exception as ai_err:
                # Defensive parsing: one malformed model output or validation crash doesn't blow up the batch
                logging.error(f"Skipping article analysis for '{article.title[:30]}': {str(ai_err)}")
                continue

        # Commit curation batch atomically
        if pending_curated_records:
            try:
                db.add_all(pending_curated_records)
                db.commit()
                logging.info(f"Successfully processed and committed {len(pending_curated_records)} curation profiles.")
            except Exception as batch_cur_err:
                db.rollback()
                logging.error(f"Curation warehouse batch commit error: {str(batch_cur_err)}")

        # ======================================================================
        # PHASE 4: DISPATCH EVALUATION MATRIX
        # ======================================================================
        logging.info("Evaluating message delivery conditions...")
        time_threshold = datetime.utcnow() - timedelta(hours=LOOKBACK_HOURS)
        
        recent_curated_exists = db.query(CuratedArticle).filter(
            CuratedArticle.created_at >= time_threshold
        ).first() is not None

        if (new_scraped_entries > 0) or recent_curated_exists:
            logging.info("Dispatch authorization verified. Compiling template layer...")
            from app.services.email_service import EmailNotificationService
            
            try:
                mailer = EmailNotificationService()
                mailer.send_daily_briefing(recipient_email=MY_INBOX)
                logging.info("Automated Engineering Intelligence Pipeline completed. Delivery dispatched.")
            except Exception as mail_err:
                logging.error(f"Notification infrastructure gateway failure: {str(mail_err)}")
        else:
            logging.info("Data pipeline idle: No new activity detected in 24 hours. Email suspended cleanly.")

    except Exception as pipeline_fatal:
        logging.critical(f"Catastrophic Pipeline Loop Failure: {str(pipeline_fatal)}")
    finally:
        db.close()
        logging.info("PostgreSQL context wrapper safely returned to Render pool connection manager.")

if __name__ == "__main__":
    run_ingestion_pipeline()