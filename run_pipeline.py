import sys
import os
from datetime import datetime, timedelta
import logging

sys.path.append(os.getcwd())

from app.database.models import init_db, SessionLocal, ScrapedArticle, CuratedArticle
from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.blog_scraper import BlogScraper
from app.services.curator_service import AICuratorService
from app.services.email_service import EmailNotificationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOOKBACK_HOURS = 24
DEFAULT_MAX_AGE_HOURS = 48
DEFAULT_YT_LIMIT = 2
MY_INBOX = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com")

TARGET_SOURCES = [
    {"name": "Google Developers Blog", "url": "https://feeds.feedburner.com/GCPCloudBlog", "category": "Google Tech & AI", "parser_type": "rss", "max_age_hours": DEFAULT_MAX_AGE_HOURS},
    {"name": "Google DeepMind Research", "url": "https://deepmind.google/blog/rss.xml", "category": "Artificial Intelligence", "parser_type": "rss", "max_age_hours": DEFAULT_MAX_AGE_HOURS},
    {"name": "AWS Architecture", "url": "https://aws.amazon.com/blogs/architecture/feed/", "category": "Cloud Architecture", "parser_type": "rss", "max_age_hours": DEFAULT_MAX_AGE_HOURS},
    {"name": "GitHub Engineering", "url": "https://github.blog/category/engineering/feed/", "category": "Software Engineering", "parser_type": "rss", "max_age_hours": DEFAULT_MAX_AGE_HOURS},
    {"name": "Netflix Tech Blog", "url": "https://netflixtechblog.com/feed", "category": "Systems Design", "parser_type": "rss", "max_age_hours": DEFAULT_MAX_AGE_HOURS},
    {"name": "Matthew Berman", "url": "@matthew_berman", "category": "AI & Automation", "parser_type": "youtube", "max_limit": DEFAULT_YT_LIMIT}
]

def run_ingestion_pipeline():
    logging.info("Initializing database schemas...")
    init_db()
    
    db = SessionLocal()
    curator = AICuratorService()
    mailer = EmailNotificationService()
    
    new_scraped_entries = 0
    all_items = []
    
    try:
        blog_worker = BlogScraper()
        logging.info("Processing configured ingestion sources...")
        
        for source in TARGET_SOURCES:
            logging.info(f"Polling Source: {source['name']} [{source['category']}]")
            try:
                if source["parser_type"] == "rss":
                    articles = blog_worker.fetch_recent_articles(target_url=source["url"], max_age_hours=source["max_age_hours"])
                    all_items.extend(articles)
                elif source["parser_type"] == "youtube":
                    yt_worker = YouTubeScraper(channel_ids=[source["url"]])
                    videos = yt_worker.fetch_recent_videos(max_limit=source["max_limit"])
                    all_items.extend(videos)
            except Exception as e:
                logging.error(f"Skipping source {source['name']}: {str(e)}")

        logging.info(f"Evaluating deduplication boundaries for {len(all_items)} fetched entries...")
        pending_scraped_records = []
        
        for item in all_items:
            existing = db.query(ScrapedArticle).filter(ScrapedArticle.article_id == item.article_id).first()
            if existing:
                continue
                
            content_body = item.raw_content
            if item.source_id.startswith('@') and not content_body:
                logging.info(f" -> Fetching transcript for: '{item.title[:40]}...'")
                try:
                    yt_trans_worker = YouTubeScraper(channel_ids=[item.source_id])
                    content_body = yt_trans_worker.get_transcript(item.article_id)
                except Exception as tx_err:
                    logging.error(f"Transcript missing for {item.article_id}: {str(tx_err)}")
                    continue
                    
            pending_scraped_records.append(ScrapedArticle(
                source_id=item.source_id, article_id=item.article_id,
                title=item.title, url=item.url, raw_content=content_body,
                published_at=item.published_at.replace(tzinfo=None)
            ))

        if pending_scraped_records:
            try:
                db.add_all(pending_scraped_records)
                db.commit()
                new_scraped_entries = len(pending_scraped_records)
                logging.info(f"Saved {new_scraped_entries} net-new rows to database.")
            except Exception as batch_db_err:
                db.rollback()
                logging.error(f"Database batch storage failure: {str(batch_db_err)}")
        else:
            logging.info("Zero net-new entries detected at ingestion border.")

        logging.info("Scanning for uncurated entries awaiting analysis...")
        uncurated_records = db.query(ScrapedArticle).filter(
            ~ScrapedArticle.id.in_(db.query(CuratedArticle.scraped_article_id))
        ).all()
        
        pending_curation_records = []
        for article in uncurated_records:
            logging.info(f" -> Submitting contract to Gemini for: '{article.title[:40]}...'")
            try:
                analysis = curator.analyze_content(article.title, article.raw_content)
                tech_stack_str = ", ".join(analysis.tech_stack) if analysis.tech_stack else "None"
                
                pending_curation_records.append(CuratedArticle(
                    scraped_article_id=article.id, summary=analysis.summary,
                    tech_stack=tech_stack_str, impact_score=analysis.impact_score,
                    justification=analysis.justification
                ))
            except Exception as ai_err:
                logging.error(f"Analysis contract dropped for '{article.title[:30]}': {str(ai_err)}")
                continue

        if pending_curation_records:
            try:
                db.add_all(pending_curation_records)
                db.commit()
                logging.info(f"Committed {len(pending_curation_records)} AI records.")
            except Exception as batch_cur_err:
                db.rollback()
                logging.error(f"Warehouse transaction commit error: {str(batch_cur_err)}")

        # PHASE 4: STRUCTURAL DECOUPLED DISPATCH MATRIX
        logging.info("Evaluating message delivery conditions...")
        
        if new_scraped_entries > 0:
            logging.info(f"Detected {new_scraped_entries} net-new rows. Dispatching standard digest...")
            try:
                mailer.send_daily_briefing(recipient_email=MY_INBOX)
                logging.info("Briefing successfully pushed to gateway.")
            except Exception as mail_err:
                logging.error(f"Notification infrastructure failure: {str(mail_err)}")
        else:
            logging.info("Ingestion delta is zero. Dispatching pipeline status pulse alert...")
            idle_html_payload = """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e1e4e6; padding: 20px; border-radius: 6px;">
                <h2 style="color: #1a1f2c; margin-top: 0;">🔄 Pipeline Pulse: System Active</h2>
                <p style="color: #4a5568; line-height: 1.5;">Your database deduplication layer successfully filtered out all incoming streams during this execution cycle because no new updates have been published since the last sync window.</p>
                <hr style="border: 0; border-top: 1px solid #e1e4e6; margin: 20px 0;"/>
                <h3 style="color: #2d3748;">🎯 High-Signal Fallback Matrices:</h3>
                <ul style="padding-left: 20px; color: #3182ce; line-height: 1.8;">
                    <li><a href="https://developers.googleblog.com/" style="text-decoration: none; color: #3182ce;">Google Developers Updates</a></li>
                    <li><a href="https://deepmind.google/blog/" style="text-decoration: none; color: #3182ce;">Google DeepMind Research Streams</a></li>
                    <li><a href="https://news.ycombinator.com/" style="text-decoration: none; color: #3182ce;">Hacker News Threads</a></li>
                </ul>
                <p style="font-size: 11px; color: #a0aec0; margin-top: 30px; text-align: center;">Automated Engineering Intelligence Pipeline • Operational</p>
            </div>
            """
            import resend
            resend.api_key = os.getenv("RESEND_API_KEY")
            try:
                resend.Emails.send({
                    "from": "onboarding@resend.dev", "to": MY_INBOX,
                    "subject": "🔄 Pipeline Pulse: No New Engineering Streams Detected", "html": idle_html_payload
                })
                logging.info("Status fallback notification sent successfully.")
            except Exception as fallback_err:
                logging.error(f"Failed to deliver fallback pulse: {str(fallback_err)}")

    except Exception as pipeline_fatal:
        logging.critical(f"Catastrophic Pipeline Loop Failure: {str(pipeline_fatal)}")
    finally:
        db.close()
        logging.info("PostgreSQL context safely released back to pool.")

if __name__ == "__main__":
    run_ingestion_pipeline()
