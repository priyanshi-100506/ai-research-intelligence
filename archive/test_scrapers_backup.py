from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.blog_scraper import BlogScraper

if __name__ == "__main__":
    print("--- 1. Testing Corporate Blog Extraction ---")
    blog_worker = BlogScraper()
    articles = blog_worker.fetch_recent_articles(max_age_hours=168)
    print(f"Successfully tracked {len(articles)} company updates.")
    for a in articles[:2]:
        print(f" -> [{a.source_id.upper()}] {a.title}")

    print("\n--- 2. Testing YouTube Live Extraction Pipeline ---")
    # Change the raw string hash directly to the clean channel handle string
    berman_channel = "@matthew_berman"
    yt_worker = YouTubeScraper(channel_ids=[berman_channel])
    
    videos = yt_worker.fetch_recent_videos()
    print(f"Successfully connected to YouTube grid layout. Found {len(videos)} total video listings.")
    
    if videos:
        sample_video = videos[0]
        print(f"Attempting live transcript parsing for latest release: '{sample_video.title}'")
        text = yt_worker.get_transcript(sample_video.article_id)
        if text:
            print(f" -> Success! Transcript Extract: {text[:150]}...")