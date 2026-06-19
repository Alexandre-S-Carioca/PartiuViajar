import logging
from events.bus import event_bus
from workers.tasks import save_flights_task
from domain.entities import Flight
from typing import List

logger = logging.getLogger(__name__)

async def handle_flight_search_completed(event_data: dict):
    logger.info(f"Event Received: FlightSearchCompleted - Cache Hit: {event_data.get('cache_hit')}")
    flights_data = event_data.get("flights", [])
    # Dispara background task via Dramatiq para salvar
    if flights_data:
        try:
            # We must serialize the flight domain entities back to dicts to pass to Dramatiq
            serialized_flights = []
            for f in flights_data:
                # f is a dict here since we serialize it before event or it's a domain object.
                # It's better to pass dicts.
                pass
            
            save_flights_task.send(flights_data)
        except Exception as e:
            logger.error(f"Error scheduling save_flights_task: {e}")

async def handle_cache_miss(event_data: dict):
    logger.info(f"Event Received: CacheMiss - Key: {event_data.get('cache_key')}")

async def handle_cache_hit(event_data: dict):
    logger.info(f"Event Received: CacheHit - Key: {event_data.get('cache_key')}")

async def handle_collector_failed(event_data: dict):
    logger.error(f"Event Received: CollectorFailed - Collector: {event_data.get('collector_name')}, Error: {event_data.get('error')}")

def register_handlers():
    event_bus.subscribe("FlightSearchCompleted", handle_flight_search_completed)
    event_bus.subscribe("CacheMiss", handle_cache_miss)
    event_bus.subscribe("CacheHit", handle_cache_hit)
    event_bus.subscribe("CollectorFailed", handle_collector_failed)
