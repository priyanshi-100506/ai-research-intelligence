import sys
import os
from datetime import datetime
from app.database.models import init_db, SessionLocal, ScrapedArticle, CuratedArticle
from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.blog_scraper import BlogScraper
from app.services.curator_service import AICuratorService

def run_ingestion_pipeline():
    print("Initializing database schemas...")
    init_db()
    
    db = SessionLocal()
    curator = AICuratorService()
    
    # --- PHASE 1: INGESTION ---
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
            
    print(f"=== Ingestion Phase Done! Saved: {saved_count} | Duplicates Skipped: {skipped_count} ===")

    # --- PHASE 2: AI CURATION ---
    print("\n--- Running AI Curation Processing Engine ---")
    # Grab all raw articles that do NOT have a matching entry in the curated table yet
    uncurated_records = db.query(ScrapedArticle).filter(
        ~ScrapedArticle.id.in_(db.query(CuratedArticle.scraped_article_id))
    ).all()
    
    print(f"Found {len(uncurated_records)} uncurated records awaiting analysis.")
    
    curated_count = 0
    for article in uncurated_records:
        print(f" -> Analyzing: '{article.title[:50]}...'")
        
        # Pass data to our Gemini Service agent loop
        analysis = curator.analyze_content(article.title, article.raw_content)
        
        # Turn list fields into database-friendly string tokens smoothly
        tech_stack_str = ", ".join(analysis.tech_stack) if analysis.tech_stack else "None"
        
        new_curated = CuratedArticle(
            scraped_article_id=article.id,
            summary=analysis.summary,
            tech_stack=tech_stack_str,
            impact_score=analysis.impact_score,
            justification=analysis.justification
        )
        
        try:
            db.add(new_curated)
            db.commit()
            curated_count += 1
            print(f"    [Success] Curated with Impact Score: {analysis.impact_score}/10")
        except Exception as e:
            db.rollback()
            print(f"    [Error] Failed to write curated row: {str(e)}")
            
    db.close()
    print(f"\n=== Pipeline Engine Finished! Total Processed Items: {curated_count} ===")

if __name__ == "__main__":
    run_ingestion_pipeline()