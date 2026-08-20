import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.ai_news_aggregator.config import settings
from src.ai_news_aggregator.database.models import Base, engine
from src.ai_news_aggregator.routers import dashboard, api, stream
from src.ai_news_aggregator.services.scheduler import scheduler, setup_scheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ── Rate Limiter (shared instance imported by routers) ──────────────────────
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")

    setup_scheduler()
    scheduler.start()
    logger.info("APScheduler initialized & started.")

    yield

    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shutdown.")
    await engine.dispose()
    logger.info("Database connection disposed.")

app = FastAPI(
    title="Metis — AI Research Intelligence API",
    description="FastAPI backend for the Metis AI research curation platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Rate Limiting Middleware ────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ────────────────────────────────────────────────────────────────────
_base_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_extra_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
origins = _base_origins + _extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(dashboard.router)
app.include_router(api.router)
app.include_router(stream.router)