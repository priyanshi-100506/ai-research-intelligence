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
from app.services.email_service import EmailNotificationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CENTRAL SETTINGS
LOOKBACK_HOURS = 24
MY_INBOX = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com")

TARGET_SOURCES = [
    {"name": "Google Developers Blog", "url": "https://feeds.feedburner.com/GCPCloudBlog", "category": "AI & Cloud Platforms", "parser_type": "rss"},
    {"name": "AWS Architecture", "url": "https://aws.amazon.com/blogs/architecture/feed/", "category": "Cloud Architecture", "parser_type": "rss"},
    {"name": "GitHub Engineering", "url": "https://github.blog/category/engineering/feed/", "category": "Software Engineering", "parser_type": "rss"},
    {"name": "Netflix Tech Blog", "url": "https://netflixtechblog.com/feed", "category": "Systems Design", "parser_type": "rss"},
    {"name": "Matthew Berman", "url": "@matthew_berman", "category": "AI Tools", "parser_type": "youtube"}
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
        # Phase 1: Ingestion Loop
        blog_worker = BlogScraper()
        for source in TARGET_SOURCES:
            try:
                if source["parser_type"] == "rss":
                    articles = blog_worker.fetch_recent_articles(target_url=source["url"], max_age_hours=48)
                    all_items.extend(articles)
                elif source["parser_type"] == "youtube":
                    yt_worker = YouTubeScraper(channel_ids=[source["url"]])
                    videos = yt_worker.fetch_recent_videos(max_limit=2)
                    all_items.extend(videos)
            except Exception as e:
                logging.error(f"Skipping source {source['name']}: {str(e)}")

        # Phase 2: Deduplication and Storage
        pending_records = []
        for item in all_items:
            existing = db.query(ScrapedArticle).filter(ScrapedArticle.article_id == item.article_id).first()
            if not existing:
                content_body = item.raw_content
                if item.source_id.startswith('@') and not content_body:
                    try:
                        yt_trans = YouTubeScraper(channel_ids=[item.source_id])
                        content_body = yt_trans.get_transcript(item.article_id)
                    except:
                        continue
                
                pending_records.append(ScrapedArticle(
                    source_id=item.source_id, article_id=item.article_id,
                    title=item.title, url=item.url, raw_content=content_body,
                    published_at=item.published_at.replace(tzinfo=None)
                ))

        if pending_records:
            db.add_all(pending_records)
            db.commit()
            new_scraped_entries = len(pending_records)
            logging.info(f"Committed {new_scraped_entries} net-new source records.")

        # Phase 3: AI Curation Engine
        uncurated_records = db.query(ScrapedArticle).filter(
            ~ScrapedArticle.id.in_(db.query(CuratedArticle.scraped_article_id))
        ).all()
        
        pending_curations = []
        for article in uncurated_records:
            try:
                analysis = curator.analyze_content(article.title, article.raw_content)
                tech_stack_str = ", ".join(analysis.tech_stack) if analysis.tech_stack else "None"
                pending_curations.append(CuratedArticle(
                    scraped_article_id=article.id, summary=analysis.summary,
                    tech_stack=tech_stack_str, impact_score=analysis.impact_score,
                    justification=analysis.justification
                ))
            except Exception as ai_err:
                logging.error(f"Analysis failed for {article.title}: {str(ai_err)}")

        if pending_curations:
            db.add_all(pending_curations)
            db.commit()

        # Phase 4: Dynamic Dispatch Matrix
        time_threshold = datetime.utcnow() - timedelta(hours=LOOKBACK_HOURS)
        has_recent_articles = db.query(CuratedArticle).filter(CuratedArticle.created_at >= time_threshold).first() is not None

        if has_recent_articles:
            logging.info("New intelligence detected. Dispatching standard briefing...")
            mailer.send_daily_briefing(recipient_email=MY_INBOX)
        else:
            # 🔄 FALLBACK GATEWAY: Send an explicit status alert instead of halting silently
            logging.info("No fresh data streams found. Dispatching pipeline status briefing...")
            
            idle_html_payload = """
            <h2>Pipeline Pulse: Status Active</h2>
            <p>Your database deduplication layer rejected all incoming streams today because no new articles or videos have been published in the last 24 hours.</p>
            <hr/>
            <h3>🎯 High-Signal Fallback Recommendations:</h3>
            <ul>
                <li><a href="https://developers.googleblog.com/">Google Developers Core Updates</a></li>
                <li><a href="https://news.ycombinator.com/">Hacker News (Top Engineering Threads)</a></li>
                <li><a href="https://tldr.tech/developer">TLDR Web Dev Archive</a></li>
            </ul>
            <p style="font-size: 11px; color: #888;">Data Loop Current • Powered by your Automated Engineering Intelligence Pipeline.</p>
            """
            
            # Using your existing resend connection inside mailer to send the update
            import resend
            resend.api_key = os.getenv("RESEND_API_KEY")
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": MY_INBOX,
                "subject": "🔄 Pipeline Pulse: No New Engineering Streams Detected",
                "html": idle_html_payload
            })
            logging.info("Status fallback notification sent successfully.")

    except Exception as pipeline_fatal:
        logging.critical(f"Catastrophic failure loop: {str(pipeline_fatal)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_ingestion_pipeline()