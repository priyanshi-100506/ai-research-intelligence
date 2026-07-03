import os
import sys
import httpx
import asyncio
import logging
import resend

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

TECH_DOMAINS = ["Large Language Models", "System Design Architecture", "Cloud Infrastructure"]
MY_INBOX = os.getenv("RECIPIENT_EMAIL", "priyanshicshah@gmail.com")
currents_key = os.getenv("NEWS_API_KEY")
resend_key = os.getenv("RESEND_API_KEY")

async def fetch_realtime_news(client, keyword, api_key):
    url = "https://api.currentsapi.services/v1/search"
    params = {"keywords": keyword, "language": "en", "apiKey": api_key}
    try:
        res = await client.get(url, params=params)
        if res.status_code == 200:
            return res.json().get("news", [])
    except Exception as e:
        logging.error(f"Scraper error: {e}")
    return []

async def main():
    logging.info("⚡ FORCING REAL-TIME DELIVERY PASS...")
    
    all_articles = []
    async with httpx.AsyncClient() as client:
        tasks = [fetch_realtime_news(client, kw, currents_key) for kw in TECH_DOMAINS]
        results = await asyncio.gather(*tasks)
        for batch in results:
            if batch: all_articles.extend(batch)

    if all_articles:
        logging.info(f"✅ Successfully grabbed {len(all_articles)} live stories from the wire. Dispatching top 3 immediately...")
        resend.api_key = resend_key
        
        html_items = ""
        seen_urls = set()
        for art in all_articles:
            url = art.get("url")
            if url in seen_urls: continue
            seen_urls.add(url)
            
            html_items += f"""
            <div style='margin-bottom: 20px; padding: 15px; background: #f8fafc; border-left: 4px solid #4f46e5; border-radius: 4px;'>
                <h4 style='margin:0 0 5px 0;'><a href='{url}' style='color:#1e293b; text-decoration:none; font-weight:bold;'>{art.get("title")}</a></h4>
                <p style='color:#475569; font-size:13px; margin:0;'>{art.get("description")}</p>
            </div>
            """
            if len(seen_urls) >= 3: break
            
        email_body = f"""
        <html>
            <body style="font-family: sans-serif; color: #1e293b; padding: 20px;">
                <h2 style="color: #4f46e5; margin-top: 0;">⚡ Live Technical News Drop (Force Pass)</h2>
                <p style="font-size: 14px; color: #64748b;">Here is the active stream data currently on the wire:</p>
                {html_items}
            </body>
        </html>
        """
        
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": MY_INBOX,
            "subject": "⚡ Live Technical Drop: Forced Verification Pass",
            "html": email_body
        })
        logging.info("🎉 Verification email dispatched successfully!")
    else:
        logging.warning("❌ No news found on the wire.")

if __name__ == "__main__":
    asyncio.run(main())
