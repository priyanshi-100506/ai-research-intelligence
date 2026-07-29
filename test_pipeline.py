import asyncio
from src.ai_news_aggregator.services.pipeline_service import PipelineService

async def test_pipeline():
    print('🚀 Testing Pipeline logic...')
    try:
        # Assuming the class is named PipelineService
        service = PipelineService()
        # We call the method
        await service.run_pipeline()
        print('✅ Pipeline completed successfully.')
    except Exception as e:
        print(f'❌ Pipeline failed: {e}')

if __name__ == '__main__':
    asyncio.run(test_pipeline())
