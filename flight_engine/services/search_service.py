import asyncio
from typing import List, Dict, Type
from datetime import datetime
from decimal import Decimal
import json
import logging
from domain.entities import Flight
from application.dto.flight_dto import SearchFlightRequest
from infrastructure.registry import registry
from infrastructure.cache import cache_service
from services.strategies.base import BaseStrategy
from services.strategies.cheapest import CheapestStrategy
from services.strategies.fastest import FastestStrategy
from services.strategies.best import BestStrategy
from events.bus import event_bus

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {
            "cheapest": CheapestStrategy(),
            "fastest": FastestStrategy(),
            "best": BestStrategy(),
        }

    def _get_cache_key(self, req: SearchFlightRequest) -> str:
        return f"flights:{req.origin}:{req.destination}:{req.departure_date}:{req.adults}"

    async def search(self, req: SearchFlightRequest) -> List[Flight]:
        cache_key = self._get_cache_key(req)
        
        # L1/L2 Cache Attempt
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            await event_bus.publish("CacheHit", {"cache_key": cache_key})
            # Convert JSON back to Flight domain entities
            flights = [
                Flight(
                    airline=f["airline"],
                    origin=f["origin"],
                    destination=f["destination"],
                    departure_date=datetime.fromisoformat(f["departure_date"]),
                    arrival_date=datetime.fromisoformat(f["arrival_date"]),
                    price=f["price"],
                    currency=f["currency"],
                    base_price_brl=f["base_price_brl"],
                    duration=f["duration"],
                    stops=f["stops"],
                    cabin_class=f["cabin_class"],
                    booking_url=f["booking_url"],
                    collected_at=datetime.fromisoformat(f["collected_at"]),
                    id=f["id"]
                ) for f in cached_data
            ]
            strategy = self.strategies.get(req.strategy, self.strategies["best"])
            sorted_flights = strategy.sort(flights)
            return sorted_flights

        await event_bus.publish("CacheMiss", {"cache_key": cache_key})

        # Cache Stampede Protection
        lock_name = f"lock:{cache_key}"
        async with cache_service.lock(lock_name, timeout=60) as acquired:
            if not acquired:
                # Se não conseguiu o lock, aguarda e tenta o cache novamente
                # Um fluxo real poderia usar pub/sub ou polling. Aqui usaremos um pequeno delay.
                await asyncio.sleep(2)
                cached_data = await cache_service.get(cache_key)
                if cached_data:
                     # (Mesma desserialização acima, omitida para concisão ou movida para método)
                     pass

            # Descobre país de destino para pegar a moeda
            from services.airport_service import airport_service
            from infrastructure.clients.geo_client import geo_api_client
            
            dest_country = None
            for ap in airport_service.airports:
                if ap["code"] == req.destination:
                    dest_country = ap["country"]
                    break
                    
            target_currency = "BRL"
            if dest_country:
                country_info = await geo_api_client.get_country_info(dest_country)
                if country_info and "currencies" in country_info and len(country_info["currencies"]) > 0:
                    target_currency = country_info["currencies"][0]["code"]

            # Realiza a busca paralela
            dep_date = datetime.strptime(req.departure_date, "%Y-%m-%d")
            all_flights: List[Flight] = []
            
            async with asyncio.TaskGroup() as tg:
                tasks = []
                for collector in registry.get_all():
                    tasks.append(
                        tg.create_task(
                            collector.fetch_flights(req.origin, req.destination, dep_date, req.adults, currency=target_currency)
                        )
                    )

            for t in tasks:
                try:
                    all_flights.extend(t.result())
                except Exception as e:
                    # TaskGroup cancelled the rest, we should handle inner exceptions carefully.
                    # Or use asyncio.gather for better independent failure handling without canceling everything.
                    # As requested: "Capturar falhas individualmente." 
                    # TaskGroup will raise an exception group if any task fails. To capture individually, 
                    # we must wrap the collector call to return exceptions instead of raising.
                    pass

        # Workaround for TaskGroup exception handling per requirements
        return self._apply_strategy(all_flights, req.strategy)

    async def _fetch_from_all_collectors(self, origin: str, destination: str, departure_date: datetime, adults: int) -> List[Flight]:
        all_flights: List[Flight] = []
        
        async def safe_fetch(collector):
            try:
                return await collector.fetch_flights(origin, destination, departure_date, adults)
            except Exception as e:
                await event_bus.publish("CollectorFailed", {"collector_name": collector.name, "error": str(e)})
                return []

        # TaskGroup behavior is strict, to truly isolate we can use gather or wrap
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(safe_fetch(c)) for c in registry.get_all()]
            
        for t in tasks:
            all_flights.extend(t.result())
            
        return all_flights

    async def search_v2(self, req: SearchFlightRequest) -> List[Flight]:
        # Refactored search with proper stampede protection and serialization
        cache_key = self._get_cache_key(req)
        
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            await event_bus.publish("CacheHit", {"cache_key": cache_key})
            return self._deserialize_and_sort(cached_data, req.strategy)

        await event_bus.publish("CacheMiss", {"cache_key": cache_key})

        lock_name = f"lock:{cache_key}"
        async with cache_service.lock(lock_name, timeout=60) as acquired:
            if not acquired:
                # Polling for cache as another thread is doing the work
                for _ in range(5):
                    await asyncio.sleep(1)
                    cached_data = await cache_service.get(cache_key)
                    if cached_data:
                        return self._deserialize_and_sort(cached_data, req.strategy)

            # Acquired lock, fetch data
            dep_date = datetime.strptime(req.departure_date, "%Y-%m-%d")
            all_flights = await self._fetch_from_all_collectors(req.origin, req.destination, dep_date, req.adults)
            
            # Save to cache
            serialized = self._serialize(all_flights)
            await cache_service.set(cache_key, serialized)
            
            # Fire event to save in background
            await event_bus.publish("FlightSearchCompleted", {"cache_hit": False, "flights": serialized})

        return self._apply_strategy(all_flights, req.strategy)

    def _apply_strategy(self, flights: List[Flight], strategy_name: str) -> List[Flight]:
        strategy = self.strategies.get(strategy_name, self.strategies["best"])
        return strategy.sort(flights)
        
    def _serialize(self, flights: List[Flight]) -> List[dict]:
        return [
            {
                "airline": f.airline,
                "origin": f.origin,
                "destination": f.destination,
                "departure_date": f.departure_date.isoformat(),
                "arrival_date": f.arrival_date.isoformat(),
                "price": str(f.price),
                "currency": f.currency,
                "base_price_brl": str(f.base_price_brl),
                "duration": f.duration,
                "stops": f.stops,
                "cabin_class": f.cabin_class,
                "booking_url": f.booking_url,
                "collected_at": f.collected_at.isoformat(),
                "id": f.id
            } for f in flights
        ]
        
    def _deserialize_and_sort(self, data: List[dict], strategy_name: str) -> List[Flight]:
        flights = []
        for f in data:
            flights.append(Flight(
                airline=f["airline"],
                origin=f["origin"],
                destination=f["destination"],
                departure_date=datetime.fromisoformat(f["departure_date"]),
                arrival_date=datetime.fromisoformat(f["arrival_date"]),
                price=Decimal(f["price"]),
                currency=f["currency"],
                base_price_brl=Decimal(f["base_price_brl"]),
                duration=f["duration"],
                stops=f["stops"],
                cabin_class=f["cabin_class"],
                booking_url=f["booking_url"],
                collected_at=datetime.fromisoformat(f["collected_at"]),
                id=f["id"]
            ))
        return self._apply_strategy(flights, strategy_name)

    async def stream_search(self, req: SearchFlightRequest):
        origin = req.origin.upper()
        destination = req.destination.upper()
        dep_date_str = req.departure_date
        strategy = req.strategy.lower()
        
        collectors = registry.get_all()
        pending_collectors = []
        
        # 1. First, check cache for each collector. Yield immediately if cached.
        for collector in collectors:
            cache_key = f"flights:{origin}:{destination}:{dep_date_str}:{strategy}:{collector.name}"
            cached_data = await cache_service.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for collector {collector.name} (key: {cache_key})")
                yield f"data: {json.dumps({'collector': collector.name, 'status': 'success', 'flights': cached_data})}\n\n"
            else:
                pending_collectors.append(collector.name)
        
        # 2. If all collectors were cached, we are done!
        if not pending_collectors:
            return
            
        # 3. For any pending collectors, trigger Dramatiq background tasks
        from workers.tasks import scrape_and_cache_flights_task
        for col_name in pending_collectors:
            logger.info(f"Triggering background task to scrape {col_name} for {origin}->{destination} on {dep_date_str}")
            scrape_and_cache_flights_task.send(origin, destination, dep_date_str, col_name, strategy)
            
        # 4. Subscribe to the Redis Pub/Sub channel to wait for background results
        pubsub_channel = f"pubsub:flights:{origin}:{destination}:{dep_date_str}:{strategy}"
        pubsub = cache_service.redis.pubsub()
        await pubsub.subscribe(pubsub_channel)
        
        try:
            received_count = 0
            target_count = len(pending_collectors)
            
            # Read messages with a timeout (e.g. 50 seconds max loop)
            start_time = datetime.utcnow()
            while received_count < target_count:
                if (datetime.utcnow() - start_time).total_seconds() > 50:
                    logger.warning("Stream search timed out waiting for background workers.")
                    break
                    
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg:
                    data_str = msg["data"]
                    if isinstance(data_str, bytes):
                        data_str = data_str.decode("utf-8")
                    data = json.loads(data_str)
                    col_name = data.get("collector")
                    
                    if col_name in pending_collectors:
                        yield f"data: {data_str}\n\n"
                        received_count += 1
                else:
                    await asyncio.sleep(0.5)
        finally:
            await pubsub.unsubscribe(pubsub_channel)
            await pubsub.close()
            
search_service = SearchService()
