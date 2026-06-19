import sys
import os
import asyncio
import json
from datetime import datetime

# Set up python path so we can import from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from infrastructure.registry import registry
from infrastructure.cache import cache_service
from workers.tasks import save_flights_async

# Register collectors
from infrastructure.collectors.google_flights_collector import GoogleFlightsCollector
from infrastructure.collectors.kayak_collector import KayakCollector

try:
    registry.get("GoogleFlights(Real)")
except KeyError:
    registry.register(GoogleFlightsCollector())

try:
    registry.get("Kayak(Real)")
except KeyError:
    registry.register(KayakCollector())

async def main():
    if len(sys.argv) < 6:
        print("Usage: run_scraper.py <origin> <destination> <date> <collector_name> <strategy>")
        sys.exit(1)
        
    origin = sys.argv[1].upper()
    destination = sys.argv[2].upper()
    departure_date_str = sys.argv[3]
    collector_name = sys.argv[4]
    strategy = sys.argv[5].lower()
    
    print(f"Scraper process started for {collector_name} ({origin}->{destination} on {departure_date_str})")
    
    dep_date = datetime.strptime(departure_date_str, "%Y-%m-%d")
    pubsub_channel = f"pubsub:flights:{origin}:{destination}:{departure_date_str}:{strategy}"
    
    try:
        collector = registry.get(collector_name)
        flights = await collector.fetch_flights(origin, destination, dep_date, 1)
        
        # Serialize flights
        serialized = [
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
        
        # Save to cache
        cache_key = f"flights:{origin}:{destination}:{departure_date_str}:{strategy}:{collector_name}"
        await cache_service.set(cache_key, serialized)
        
        # Save to database
        if serialized:
            await save_flights_async(serialized)
            
        # Publish success to Pub/Sub
        payload = {
            "collector": collector_name,
            "status": "success",
            "flights": serialized
        }
        await cache_service.redis.publish(pubsub_channel, json.dumps(payload))
        print(f"Scraper process finished successfully for {collector_name}")
        
    except Exception as e:
        print(f"Scraper process error for {collector_name}: {e}", file=sys.stderr)
        # Publish error to Pub/Sub
        payload = {
            "collector": collector_name,
            "status": "error",
            "error": str(e)
        }
        await cache_service.redis.publish(pubsub_channel, json.dumps(payload))
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())
