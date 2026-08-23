import asyncio
from src.ai_news_aggregator.services.pipeline_service import PipelineService

async def main():
    service = PipelineService()
    result = await service.run_pipeline()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())