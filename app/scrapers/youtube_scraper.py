import yt_dlp
from datetime import datetime, timezone
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from app.scrapers.base import ArticleMetadata

class YouTubeScraper:
    def __init__(self, channel_ids: List[str]):
        """
        Initializes the YouTube scraper component.
        Accepts channel handles (e.g., '@matthew_berman') or raw channel hashes.
        """
        self.channel_ids = channel_ids

    def fetch_recent_videos(self, max_limit: int = 3) -> List[ArticleMetadata]:
        """
        Harvests the absolute latest video metadata objects from target feeds
        using enterprise flat extraction loops to bypass regional blocks.
        """
        recent_videos = []

        # Configure yt-dlp option sets to extract metadata maps only without raw multimedia files
        ydl_opts = {
            'extract_flat': True,       # Pull index streams only (lightning fast execution)
            'playlistend': max_limit,   # Limit video items grabbed per target resource
            'quiet': True,
            'skip_download': True,
        }

        for channel_id in self.channel_ids:
            try:
                # Format string targets cleanly depending on whether a handle or hash parameter is assigned
                if channel_id.startswith('@'):
                    channel_url = f"https://www.youtube.com/{channel_id}/videos"
                else:
                    channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(channel_url, download=False)
                    
                    if 'entries' in info:
                        for entry in info['entries']:
                            if not entry:
                                continue
                            
                            video_id = entry.get('id')
                            title = entry.get('title', 'Untitled Video')
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            recent_videos.append(ArticleMetadata(
                                source_id=channel_id,
                                article_id=video_id,
                                title=title,
                                url=video_url,
                                published_at=datetime.now(timezone.utc)
                            ))
            except Exception as e:
                print(f"Error accessing yt-dlp layer for channel {channel_id}: {str(e)}")
                
        return recent_videos

    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Extracts spoken captions by instantiating the library client directly 
        and maps fields to the modern object-oriented schema layout.
        """
        try:
            client = YouTubeTranscriptApi()
            transcript_data = client.fetch(video_id, languages=['en'])
            
            # Extract out the text directly from the object attribute property
            full_text = " ".join([block.text for block in transcript_data])
            return full_text
        except Exception as e:
            print(f"Skipping transcript extraction for video ID {video_id}: {str(e)}")
            return None