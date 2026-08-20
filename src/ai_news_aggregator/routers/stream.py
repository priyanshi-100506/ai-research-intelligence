import json
import asyncio
import logging
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from src.ai_news_aggregator.core.shared import broadcaster

router = APIRouter(tags=["Streaming"])
logger = logging.getLogger(__name__)

@router.get("/stream")
async def message_stream(request: Request):
    queue = broadcaster.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    # Non-blocking wait with 15s timeout for keep-alive ping
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    
                    # Send custom SSE event name matching frontend listener
                    yield f"event: new_article\ndata: {json.dumps(data)}\n\n"
                    
                except asyncio.TimeoutError:
                    # SSE comment line for keep-alive
                    yield ": keep-alive\n\n"

        except Exception as e:
            logger.error(f"Error in SSE stream: {e}", exc_info=True)
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )