from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from ai_news_aggregator.database.models import SessionLocal, CuratedArticle, ScrapedArticle

app = FastAPI()
# This tells FastAPI where to look for your index.html
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    db = SessionLocal()
    # Query your data
    articles = db.query(CuratedArticle, ScrapedArticle).join(ScrapedArticle).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "articles": articles})