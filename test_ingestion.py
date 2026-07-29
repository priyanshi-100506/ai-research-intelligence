from ai_news_aggregator.services.pipeline_service import PipelineService

service = PipelineService()
result = service.run_ingestion()
print(result)