import os
import resend
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from app.database.models import SessionLocal, ScrapedArticle, CuratedArticle

class EmailNotificationService:
    def __init__(self):
        resend.api_key = os.getenv("RESEND_API_KEY", "YOUR_RESEND_KEY")
        self.sender = "onboarding@resend.dev"

    def send_daily_briefing(self, recipient_email: str):
        db = SessionLocal()
        
        # Look back 7 days to capture your previous data runs
        time_threshold = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        
        results = (
            db.query(ScrapedArticle, CuratedArticle)
            .join(CuratedArticle, ScrapedArticle.id == CuratedArticle.scraped_article_id)
            .filter(ScrapedArticle.created_at >= time_threshold)
            .order_by(CuratedArticle.id.desc())
            .all()
        )
        
        if not results:
            logging.warning("⚠️ Email service aborted: Zero curated matching records found in Neon history.")
            db.close()
            return

        section_matrix = defaultdict(list)
        processed_article_ids = set()

        for scraped, curated in results:
            if scraped.id in processed_article_ids:
                continue
            if curated.impact_score <= 1 or (curated.justification and "RESOURCE_EXHAUSTED" in curated.justification):
                continue
                
            processed_article_ids.add(scraped.id)
            display_category = scraped.category or "General Systems Engineering"
            section_matrix[display_category].append((scraped, curated))

        sections_html_buffer = ""
        for category, articles in section_matrix.items():
            if not articles:
                continue
                
            sections_html_buffer += f"""
            <div style="margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px;">
                <h3 style="color: #4f46e5; text-transform: uppercase; font-size: 13px; font-weight: 800; letter-spacing: 0.05em; margin: 0;">
                    📁 {category}
                </h3>
            </div>
            """
            
            for scraped, curated in articles:
                stack_badges = ""
                if curated.tech_stack and curated.tech_stack != "None":
                    for tech in curated.tech_stack.split(","):
                        stack_badges += f'<span style="display: inline-block; background-color: #f1f5f9; color: #475569; font-size: 11px; font-weight: 500; padding: 2px 6px; border-radius: 4px; margin-right: 4px; font-family: monospace;">{tech.strip()}</span>'

                sections_html_buffer += f"""
                <div style="margin-bottom: 24px; padding: 16px; background-color: #ffffff; border: 1px solid #f1f5f9; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <h4 style="margin: 0; font-size: 15px; font-weight: 700; line-height: 1.4;">
                            <a href="{scraped.url}" style="color: #1e293b; text-decoration: none; border-bottom: 1px solid #cbd5e1;">{scraped.title}</a>
                        </h4>
                        <span style="font-size: 11px; font-weight: bold; color: #166534; background-color: #f0fdf4; padding: 2px 6px; border-radius: 9999px; white-space: nowrap; margin-left: 10px;">
                            Impact: {curated.impact_score}/10
                        </span>
                    </div>
                    <p style="color: #475569; font-size: 13px; line-height: 1.5; margin: 0 0 10px 0;">{curated.summary}</p>
                    <div style="margin-bottom: 8px;">{stack_badges}</div>
                    <p style="color: #64748b; font-size: 12px; font-style: italic; margin: 0; border-top: 1px dashed #f1f5f9; padding-top: 6px;">
                        <strong>Architectural Context:</strong> {curated.justification}
                    </p>
                </div>
                """

        full_email_payload = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #fafafa; padding: 20px; color: #1e293b; margin: 0;">
            <div style="max-width: 650px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="background-color: #0f172a; padding: 24px; text-align: center; color: #ffffff;">
                    <h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.025em;">🛠️ Technical Intelligence Digest</h1>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em;">Automated Multi-Domain Curation Engine</p>
                </div>
                <div style="padding: 24px; background-color: #ffffff;">
                    <p style="font-size: 13px; color: #64748b; margin-top: 0; margin-bottom: 20px;">
                        Curated high-signal engineering updates processed across tracking channels.
                    </p>
                    {sections_html_buffer}
                </div>
                <div style="background-color: #f8fafc; padding: 16px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="font-size: 11px; color: #94a3b8; margin: 0;">Zero-Cost Serverless Execution Grid • Powered by Neon PostgreSQL</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            resend.Emails.send({
                "from": self.sender,
                "to": recipient_email,
                "subject": f"🎯 Engineering Briefing: Categorized Technical Deltas",
                "html": full_email_payload
            })
            logging.info(f"🚀 SUCCESS: Newsletter sent out to {recipient_email}")
        except Exception as mail_err:
            logging.error(f"❌ Resend delivery failure: {str(mail_err)}")
            
        db.close()
