from app.services.pipeline_service import PipelineService

def run():
    service = PipelineService()
    service.execute_pipeline(send_email=True)

if __name__ == '__main__':
    run()