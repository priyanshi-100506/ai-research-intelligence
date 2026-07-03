import os
import sys
import logging
import resend
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# Set up raw terminal stdout streams so GitHub handles logs instantly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("📢 DIAGNOSTIC START: Initializing Self-Contained Test Engine...")

# Read Environment Variables
db_url = os.getenv("DATABASE_URL")
resend_key = os.getenv("RESEND_API_KEY")
target_email = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com")

logging.info(f"🔑 Env Verify - DATABASE_URL Present: {bool(db_url)}")
logging.info(f"🔑 Env Verify - RESEND_API_KEY Present: {bool(resend_key)}")
logging.info(f"🔑 Env Verify - Destination Address: {target_email}")

if not db_url or not resend_key:
    logging.error("❌ CRITICAL: Missing vital cloud environment secrets. Stopping test loop.")
    sys.exit(1)

# Configure Minimal Schema Layer to match your table names
Base = declarative_base()

class ScrapedArticle(Base):
    __tablename__ = 'scraped_articles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)

class CuratedArticle(Base):
    __tablename__ = 'curated_articles'
    id = Column(Integer, primary_key=True)
    scraped_article_id = Column(Integer, ForeignKey('scraped_articles.id'))
    summary = Column(Text)
    justification = Column(Text)

try:
    logging.info("Connecting to Neon Cloud Infrastructure...")
    engine = create_engine(db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    logging.info("Querying records from cloud tables...")
    results = (
        session.query(ScrapedArticle, CuratedArticle)
        .join(CuratedArticle, ScrapedArticle.id == CuratedArticle.scraped_article_id)
        .all()
    )
    
    logging.info(f"📊 Neon Query Success: Found total of {len(results)} rows.")
    
    # Build HTML list
    html_items = ""
    if results:
        for scraped, curated in results[:5]:
            html_items += f"<li><b>{scraped.title}</b><br/>{curated.summary}</li>"
    else:
        html_items = "<li>No elements found in table cache rows yet. This is a baseline transmission test!</li>"

except Exception as db_err:
    logging.error(f"❌ DATABASE FAILURE: Failed to communicate with Neon pool: {str(db_err)}")
    sys.exit(1)

# Dispatch Layer Verification
try:
    logging.info("Initializing Resend gateway configuration...")
    resend.api_key = resend_key
    
    email_body = f"""
    <html>
        <body>
            <h2>🚀 Pipeline Diagnostic Verification Pass</h2>
            <p>Connection from GitHub Action runner to Neon completed smoothly.</p>
            <ul>{html_items}</ul>
            <hr/>
            <small>Timestamp: {datetime.now().isoformat()}</small>
        </body>
    </html>
    """
    
    logging.info(f"Submitting payload transit request to onboarding@resend.dev -> {target_email}...")
    response = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": target_email,
        "subject": "🚀 Technical Pipeline Connection Verification",
        "html": email_body
    })
    logging.info(f"🎉 API SUCCESS! Resend accepted transit. ID reference token: {response}")

except Exception as mail_err:
    logging.error(f"❌ MAILER GATEWAY REJECTION: Resend refused or blocked request: {str(mail_err)}")

finally:
    session.close()
    logging.info("📢 DIAGNOSTIC COMPLETE: Engine wrapping up cleanly.")
