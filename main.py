import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

# Database and core imports
from src.ai_news_aggregator.database.models import Base, engine
from src.ai_news_aggregator.routers import dashboard, api, stream

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")
    yield
    # Dispose connection pool on shutdown
    await engine.dispose()
    logger.info("Database connection disposed.")

app = FastAPI(title="AI Research Intelligence Platform", lifespan=lifespan)

# Setup CORS for frontend communication
origins = [
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # React / Next.js default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates directory setup (if shared globally)
templates = Jinja2Templates(directory="src/ai_news_aggregator/templates")

# Register Modular Routers (No route definitions here!)
app.include_router(dashboard.router)
app.include_router(api.router)
app.include_router(stream.router)