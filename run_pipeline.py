import sys
import os

# Dynamic Root Resolution Layer
# This looks at the exact file location of run_pipeline.py, finds its directory folder, 
# and explicitly forces Python to treat it as the primary package look-up space.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Standard imports proceed down below...
from datetime import datetime
from app.database.models import init_db, SessionLocal, ScrapedArticle
from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.blog_scraper import BlogScraper

# ... rest of your run_pipeline.py remains exactly the same as before ...
def run_ingestion_pipeline():
    print("Initializing database schemas...")
    init_db()
    
    db = SessionLocal()
    
    print("\n--- Harvesting Tech Blog Streams ---")
    blog_worker = BlogScraper()
    blog_articles = blog_worker.fetch_recent_articles(max_age_hours=48)
    print(f"Captured {len(blog_articles)} corporate articles.")
    
    print("\n--- Harvesting YouTube Content Channels ---")
    channels = ["@matthew_berman"]
    yt_worker = YouTubeScraper(channel_ids=channels)
    yt_videos = yt_worker.fetch_recent_videos(max_limit=2)
    print(f"Indexed {len(yt_videos)} video listings from target handles.")
    
    all_items = blog_articles + yt_videos
    saved_count = 0
    skipped_count = 0
    
    print(f"\nProcessing database storage for {len(all_items)} mixed entries...")
    for item in all_items:
        existing = db.query(ScrapedArticle).filter(ScrapedArticle.article_id == item.article_id).first()
        if existing:
            skipped_count += 1
            continue
            
        content_body = item.raw_content
        if item.source_id.startswith('@') and not content_body:
            print(f" -> Fetching full audio transcript for: '{item.title}'")
            content_body = yt_worker.get_transcript(item.article_id)
            
        new_record = ScrapedArticle(
            source_id=item.source_id,
            article_id=item.article_id,
            title=item.title,
            url=item.url,
            raw_content=content_body,
            published_at=item.published_at.replace(tzinfo=None)
        )
        
        try:
            db.add(new_record)
            db.commit()
            saved_count += 1
            print(f" -> Saved successfully: {item.title[:50]}...")
        except Exception as e:
            db.rollback()
            print(f" -> Error writing record: {str(e)}")
            
    db.close()
    print(f"\n=== Ingestion Completed! Saved: {saved_count} | Duplicates Skipped: {skipped_count} ===")

if __name__ == "__main__":
    run_ingestion_pipeline()