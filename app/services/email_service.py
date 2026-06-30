import os
import resend
from datetime import datetime, timedelta, timezone
from app.database.models import SessionLocal, CuratedArticle, ScrapedArticle

class EmailNotificationService:
    def __init__(self):
        # Pulls the Resend token out of your .env file safely
        self.api_key = os.getenv("RESEND_API_KEY")
        if self.api_key:
            resend.api_key = self.api_key

    def build_newsletter_html(self, articles) -> str:
        """Generates a clean, professional HTML layout with embedded technical content tags."""
        article_sections = ""
        
        for art in articles:
            # Process comma-separated tech stack tokens into a clean list of visual items
            tags = [t.strip() for t in art.tech_stack.split(',') if t.strip() and t.strip() != 'None']
            tag_badges = "".join([
                f"<span style='background:#f1f5f9; color:#475569; padding:3px 8px; margin-right:6px; border-radius:4px; font-size:11px; font-weight:500; font-family:monospace; display:inline-block; margin-bottom:6px; border:1px solid #e2e8f0;'>{t}</span>" 
                for t in tags
            ])

            article_sections += f"""
            <div style="margin-bottom: 28px; padding-bottom: 24px; border-bottom: 1px solid #e2e8f0;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 8px;">
                    <tr>
                        <td style="font-size: 11px; font-weight: bold; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.5px;">
                            {art.scraped_article.source_id}
                        </td>
                        <td align="right" style="font-size: 11px; font-weight: bold; color: #e11d48; background: #fff1f2; padding: 2px 8px; border-radius: 4px; border: 1px solid #ffe4e6;">
                            Impact Score: {art.impact_score}/10
                        </td>
                    </tr>
                </table>
                <h3 style="margin: 0 0 10px 0; font-size: 18px; line-height: 1.4; color: #0f172a;">
                    <a href="{art.scraped_article.url}" style="color: #0f172a; text-decoration: none;">{art.scraped_article.title}</a>
                </h3>
                <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin: 12px 0; border-left: 4px solid #4f46e5;">
                    <p style="margin: 0; font-size: 14px; color: #334155; line-height: 1.6;">{art.summary}</p>
                </div>
                <p style="margin: 8px 0 14px 0; font-size: 12px; color: #64748b; line-height: 1.5;">
                    <strong style="color: #475569;">Analysis Justification:</strong> {art.justification}
                </p>
                <div style="margin-top: 8px;">{tag_badges}</div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; padding: 20px; margin: 0; -webkit-font-smoothing: antialiased;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); overflow: hidden;">
                <tr>
                    <td style="background: #0f172a; padding: 32px 24px; text-align: center;">
                        <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">Morning AI Executive Briefing</h1>
                        <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 13px;">Automated analytical synthesis of verified engine streams.</p>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 32px 24px 12px 24px;">
                        {article_sections}
                    </td>
                </tr>
                <tr>
                    <td style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8;">
                        Engine Data Loop Active • Powered by your Custom AI News Aggregator Pipeline.
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def send_daily_briefing(self, recipient_email: str):
        """Queries database for top tier records and triggers the secure Resend mail gateway."""
        if not self.api_key:
            print("⚠️ Skipped Email Dispatch: RESEND_API_KEY environment variable is missing.")
            return

        # Ensure we strip out any accidental leading/trailing spaces from the incoming email string
        target_inbox = recipient_email.strip()
        print(f"DEBUGGING TARGET EMAIL STRING: '{target_inbox}'")

        db = SessionLocal()
        time_boundary = datetime.now(timezone.utc) - timedelta(hours=72)
        
        high_impact_items = db.query(CuratedArticle).join(ScrapedArticle).filter(
            CuratedArticle.impact_score >= 7,
            CuratedArticle.created_at >= time_boundary
        ).order_by(CuratedArticle.impact_score.desc()).all()

        if not high_impact_items:
            print("ℹ️ No top tier intelligence entries (Score 7+) logged in the current target time window.")
            db.close()
            return

        print(f"📦 Compiling newsletter presentation payload for {len(high_impact_items)} high-impact records...")
        html_payload = self.build_newsletter_html(high_impact_items)

        try:
            # Fix: Pass the cleaned string directly instead of wrapping it inside a list bracket
            params = {
                "from": "onboarding@resend.dev",
                "to": target_inbox,
                "subject": f"🤖 AI Executive Briefing - {datetime.now().strftime('%d %b %Y')}",
                "html": html_payload
            }
            
            resend.Emails.send(params)
            print("🚀 Success! The curated newsletter briefing has been delivered directly to your inbox.")
        except Exception as e:
            print(f"❌ Critical Mailer Exception occurred during delivery routine: {str(e)}")
        finally:
            db.close()