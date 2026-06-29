from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.blog_scraper import BlogScraper

if __name__ == "__main__":
    print("--- 1. Testing Corporate Blog Extraction (7-Day Lookback) ---")
    blog_worker = BlogScraper()
    articles = blog_worker.fetch_recent_articles(max_age_hours=168)
    print(f"Successfully tracked {len(articles)} company updates.")
    for a in articles[:2]:
        print(f" -> [{a.source_id.upper()}] {a.title}")

    print("\n--- 2. Testing YouTube RSS & Text Extraction (7-Day Lookback) ---")
    # Matthew Berman's Channel ID (high-volume AI development updates channel)
    berman_channel = "UCv83tO5ceSyUUF17O0dWajA"
    yt_worker = YouTubeScraper(channel_ids=[berman_channel])
    
    videos = yt_worker.fetch_recent_videos(max_age_hours=168)
    print(f"Successfully tracked {len(videos)} videos on the public channel.")
    
    if videos:
        sample_video = videos[0]
        print(f"Pulling transcript dynamically for: '{sample_video.title}'")
        text = yt_worker.get_transcript(sample_video.article_id)
        if text:
            print(f" -> Success! Transcript snippet: {text[:150]}...")