import requests, resend
from datetime import datetime
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.schemas import Article

# Use the uppercase attribute names now defined in settings
resend.api_key = settings.RESEND_API_KEY
engine = create_engine(settings.DATABASE_URL)

def fetch_news(keyword):
    print(f'Fetching data for: {keyword}')
    params = {'keywords': keyword, 'language': 'en', 'apiKey': settings.NEWS_API_KEY, 'page_size': 5}
    response = requests.get('https://api.currentsapi.services/v1/search', params=params)
    response.raise_for_status()
    return response.json().get('news', [])

def send_formal_report(articles):
    if not articles: return
    table_rows = ''.join([f'<tr><td style="padding:10px; border:1px solid #ddd;">{a.title}</td><td style="padding:10px; border:1px solid #ddd;"><a href="{a.url}">Link</a></td></tr>' for a in articles])
    with open(r'app\services\email_template.html', 'r') as f:
        html = f.read().format(table_rows=table_rows)
    
    resend.Emails.send({
        'from': 'onboarding@resend.dev',
        'to': settings.RECIPIENT_EMAIL,
        'subject': 'Technical Ingestion Report',
        'html': html
    })
    print('Report dispatched successfully.')

if __name__ == '__main__':
    KEYWORDS = ['Cloud Infrastructure', 'System Design Architecture', 'Large Language Models', 'AI Agents', 'Cybersecurity', 'Database Scaling']
    keyword = KEYWORDS[datetime.now().hour % len(KEYWORDS)]
    
    try:
        raw_news = fetch_news(keyword)
        # Using the uppercase attribute names
        articles = [Article(article_id=a['id'], title=a['title'], url=a['url'], published_at=datetime.now()) for a in raw_news]
        if articles:
            send_formal_report(articles)
        else:
            print('No data retrieved this hour.')
    except Exception as e:
        print(f'Pipeline error: {e}')
