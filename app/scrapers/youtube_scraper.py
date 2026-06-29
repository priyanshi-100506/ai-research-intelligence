import feedparser
from datetime import datetime, timezone
import time
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from app.scrapers.base import ArticleMetadata

class YouTubeScraper:
    def __init__(self, channel_ids: List[str]):
        self.channel_ids = channel_ids

    def fetch_recent_videos(self, max_age_hours: int = 24) -> List[ArticleMetadata]:
        recent_videos = []
        now = datetime.now(timezone.utc)

        for channel_id in self.channel_ids:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                published_parsed = entry.published_parsed
                published_dt = datetime.fromtimestamp(time.mktime(published_parsed), timezone.utc)

                # Only harvest if it falls within our timeline window
                age_hours = (now - published_dt).total_seconds() / 3600
                if age_hours <= max_age_hours:
                    video_id = entry.yt_videoid
                    
                    recent_videos.append(ArticleMetadata(
                        source_id=channel_id,
                        article_id=video_id,
                        title=entry.title,
                        url=entry.link,
                        published_at=published_dt
                    ))
        return recent_videos

    def get_transcript(self, video_id: str) -> Optional[str]:
        """Extracts spoken captions safely without breaking on uncaptioned videos."""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([block['text'] for block in transcript_list])
            return full_text
        except Exception as e:
            print(f"Skipping transcript for video {video_id}: {str(e)}")
            return None