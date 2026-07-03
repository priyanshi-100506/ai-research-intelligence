import logging
from app.core.config import settings
import resend
from app.services.email_service import EmailNotificationService

logging.basicConfig(level=logging.INFO)

def run():
    resend.api_key = settings.RESEND_API_KEY
    service = EmailNotificationService()
    try:
        logging.info('Starting service...')
        service.send_daily_briefing(settings.RECIPIENT_EMAIL)
        logging.info('Pipeline success.')
    except Exception as e:
        logging.error(f'Pipeline failed: {e}')

if __name__ == '__main__':
    run()
