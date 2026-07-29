import os
import logging
from ai_news_aggregator.database.models import SessionLocal, ScrapedArticle, CuratedArticle

class EmailNotificationService:
    def __init__(self):
        self.sender = 'priyanshicshah100506@gmail.com'

    def send_daily_briefing(self, recipient_email: str):
        db = SessionLocal()
        try:
            results = db.query(ScrapedArticle, CuratedArticle).join(
                CuratedArticle, ScrapedArticle.id == CuratedArticle.scraped_article_id
            ).order_by(CuratedArticle.id.desc()).all()
            
            if not results:
                logging.warning("No curated rows found. Skipping email.")
                return

            table_rows = "".join([f"<tr><td>{s.title}</td><td>{s.url}</td></tr>" for s, c in results])
            template_path = os.path.join(os.path.dirname(__file__), "email_template.html")
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            payload = template.format(table_rows=table_rows)

            # --- THE ENGINEERING SWITCH ---
            if os.getenv("APP_ENV") == "production":
                import resend
                resend.api_key = os.getenv("RESEND_API_KEY")
                resend.Emails.send({"from": self.sender, "to": recipient_email, "subject": "Tech Report", "html": payload})
                logging.info("Email sent via Resend API.")
            else:
                logging.info("--- DEV MODE: Email payload generated ---")
                logging.info(f"To: {recipient_email}")
                logging.info(f"Content length: {len(payload)} characters")
                # This makes the system "talk to you" by printing the content
                logging.info(f"Payload Preview: {payload[:200]}...") 
        except Exception as e:
            logging.error(f"Failed to process email: {str(e)}")
        finally:
            db.close()
