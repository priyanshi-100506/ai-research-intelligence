import os
import resend
import logging
from app.database.models import SessionLocal, ScrapedArticle, CuratedArticle

class EmailNotificationService:
    def __init__(self):
        resend.api_key = os.getenv("RESEND_API_KEY")
        self.sender = 'onboarding@resend.dev'

    def send_daily_briefing(self, recipient_email: str):
        db = SessionLocal()
        try:
            results = db.query(ScrapedArticle, CuratedArticle).join(
                CuratedArticle, ScrapedArticle.id == CuratedArticle.scraped_article_id
            ).order_by(CuratedArticle.id.desc()).all()
            
            if not results:
                logging.warning("No curated rows found. Skipping email.")
                return

            table_rows = ""
            for scraped, curated in results:
                table_rows += f"<tr><td style='padding: 10px; border: 1px solid #ddd;'>{scraped.title}</td><td style='padding: 10px; border: 1px solid #ddd;'><a href='{scraped.url}'>Link</a></td></tr>"

            # Properly load and read the template
            template_path = os.path.join(os.path.dirname(__file__), "email_template.html")
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            full_email_payload = template.format(table_rows=table_rows)
            
            logging.info("Submitting payload to Resend gateway...")
            response = resend.Emails.send({
                "from": self.sender,
                "to": recipient_email,
                "subject": "Technical Update Report",
                "html": full_email_payload
            })
            
            print(f"DEBUG: Resend response: {response}")
            
        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}")
        finally:
            db.close()
