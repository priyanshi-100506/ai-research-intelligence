import os
import resend
import logging
from app.database.models import SessionLocal, ScrapedArticle, CuratedArticle

class EmailNotificationService:
    def __init__(self):
        resend.api_key = os.getenv("RESEND_API_KEY", "YOUR_RESEND_KEY")
        self.sender = "onboarding@resend.dev"

    def send_daily_briefing(self, recipient_email: str):
        db = SessionLocal()
        logging.info("DEBUG: Querying Neon for ANY existing curated article records...")
        
        results = (
            db.query(ScrapedArticle, CuratedArticle)
            .join(CuratedArticle, ScrapedArticle.id == CuratedArticle.scraped_article_id)
            .order_by(CuratedArticle.id.desc())
            .all()
        )
        
        if not results:
            logging.warning("⚠️ DEBUG ALERT: Found exactly 0 curated rows in your Neon database. You need to scrape new articles first!")
            db.close()
            return

        logging.info(f"✅ DEBUG: Found {len(results)} records in Neon. Building HTML template...")

        sections_html_buffer = ""
        for scraped, curated in results[:5]:
            sections_html_buffer += f"""
            <div style="margin-bottom: 20px; padding: 15px; background-color: #ffffff; border: 1px solid #f1f5f9; border-radius: 6px;">
                <h4 style="margin: 0 0 5px 0; font-size: 15px; color: #1e293b;">
                    <a href="{scraped.url}" style="color: #4f46e5; text-decoration: none;">{scraped.title}</a>
                </h4>
                <p style="color: #475569; font-size: 13px; margin: 0 0 5px 0;">{curated.summary}</p>
                <small style="color: #64748b; font-size: 11px;"><strong>Context:</strong> {curated.justification}</small>
            </div>
            """

        full_email_payload = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: sans-serif; background-color: #fafafa; padding: 20px; color: #1e293b;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px;">
                <h2 style="color: #0f172a; margin-top: 0;">🚀 Neon Cloud Pipeline Test Pass</h2>
                <p style="font-size: 13px; color: #64748b;">If you are reading this, your cloud engine can talk to Resend successfully!</p>
                {sections_html_buffer}
            </div>
        </body>
        </html>
        """

        try:
            logging.info(f"Submitting payload to Resend gateway for recipient: {recipient_email}...")
            response = resend.Emails.send({
                "from": self.sender,
                "to": recipient_email,
                "subject": "🚀 Neon Cloud Pipeline Test Pass",
                "html": full_email_payload
            })
            logging.info(f"🎉 SUCCESS! Resend accepted transaction. Message ID: {response}")
        except Exception as mail_err:
            logging.error(f"❌ Resend API threw an error: {str(mail_err)}")
            
        db.close()
