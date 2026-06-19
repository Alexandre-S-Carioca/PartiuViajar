import asyncio
from typing import List, Callable, Dict
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler for event: {event_type}")

    async def publish(self, event_type: str, event_data: dict):
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            try:
                # Dispara assincronamente (fire and forget)
                asyncio.create_task(handler(event_data))
            except Exception as e:
                logger.error(f"Error publishing event {event_type} to handler: {e}")

event_bus = EventBus()
