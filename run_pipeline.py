from app.core.logger import get_logger
from datetime import datetime
import requests, resend, os
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.schemas import Article

# Initialize logger and settings
logger = get_logger('pipeline')
resend.api_key = settings.RESEND_API_KEY
engine = create_engine(settings.DATABASE_URL)

def fetch_news(keyword):
    logger.info(f"Fetching data for: {keyword}")
    url = 'https://api.currentsapi.services/v1/search'
    params = {'keywords': keyword, 'language': 'en', 'apiKey': settings.NEWS_API_KEY, 'page_size': 5}
    
    try:
        response = requests.get(url, params=params)
        
        # Defensive Handling: Categorize failures instead of crashing
        if response.status_code == 429:
            logger.warning(f"Rate limit hit (429) for {keyword}. Skipping.")
            return []
        elif response.status_code == 403:
            logger.error(f"Access Forbidden (403) for {keyword}. Check API Key/Credits.")
            return []
            
        response.raise_for_status()
        return response.json().get('news', [])
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during fetch for {keyword}: {e}")
        return []

def send_formal_report(articles):
    if not articles: 
        logger.warning("No articles to report. Skipping email.")
        return
        
    table_rows = ''.join([f'<tr><td style="padding:10px; border:1px solid #ddd;">{a.title}</td><td style="padding:10px; border:1px solid #ddd;"><a href="{a.url}">Link</a></td></tr>' for a in articles])
    
    template_path = os.path.join('app', 'services', 'email_template.html')
    with open(template_path, 'r') as f:
        html = f.read().format(table_rows=table_rows)
    
    try:
        resend.Emails.send({
            'from': 'onboarding@resend.dev',
            'to': settings.RECIPIENT_EMAIL,
            'subject': 'Technical Ingestion Report',
            'html': html
        })
        logger.info("Report dispatched successfully.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

if __name__ == '__main__':
    KEYWORDS = ['Cloud Infrastructure', 'System Design Architecture', 'Large Language Models', 'AI Agents', 'Cybersecurity', 'Database Scaling']
    keyword = KEYWORDS[datetime.now().hour % len(KEYWORDS)]
    
    try:
        raw_news = fetch_news(keyword)
        if raw_news:
            articles = [Article(article_id=a['id'], title=a['title'], url=a['url'], published_at=datetime.now()) for a in raw_news]
            send_formal_report(articles)
        else:
            logger.info(f"Pipeline finished for {keyword} with no new data.")
    except Exception as e:
        logger.error(f"Unexpected pipeline failure: {e}")
