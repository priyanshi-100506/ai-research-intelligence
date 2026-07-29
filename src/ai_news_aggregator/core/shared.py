import asyncio
from typing import Set, Dict, Any

class NewsBroadcaster:
    def __init__(self):
        self.subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        """Register a new client listener queue."""
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Remove a client listener queue on disconnect."""
        self.subscribers.discard(queue)

    async def broadcast(self, article_data: Dict[str, Any]) -> None:
        """Push a newly summarized paper to all connected client streams."""
        for queue in list(self.subscribers):
            await queue.put(article_data)

# Global singleton instance
broadcaster = NewsBroadcaster()