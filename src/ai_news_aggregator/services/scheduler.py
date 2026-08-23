from datetime import datetime, timezone, timedelta
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.ai_news_aggregator.services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_ingestion_task():
    logger.info("⏰ APScheduler: Triggering automated paper ingestion pipeline...")
    try:
        pipeline = PipelineService()
        await pipeline.run_pipeline()
        logger.info("✅ APScheduler: Pipeline execution finished successfully.")
    except Exception as e:
        logger.error(f"❌ APScheduler: Pipeline failed: {e}", exc_info=True)

def setup_scheduler():
    scheduler.add_job(
        scheduled_ingestion_task,
        trigger=IntervalTrigger(hours=6),
        id="arxiv_ingestion_job",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=30)  # 🚀 Small delay for DB tables to init
    )