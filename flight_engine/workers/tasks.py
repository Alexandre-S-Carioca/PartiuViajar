import dramatiq
import asyncio
import logging
import json
from typing import List
from datetime import datetime
from decimal import Decimal
from workers.dramatiq_setup import redis_broker
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import FlightModel, FlightPriceHistoryModel
from infrastructure.registry import registry
from infrastructure.cache import cache_service

# Register collectors for the worker process
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

logger = logging.getLogger(__name__)

async def save_flights_async(flights_data: List[dict]):
    """Save collected flights to Postgres database using merge (upsert)."""
    async with AsyncSessionLocal() as session:
        for f in flights_data:
            # Parse dates and decimal prices
            dep_date = datetime.fromisoformat(f["departure_date"])
            arr_date = datetime.fromisoformat(f["arrival_date"])
            coll_date = datetime.fromisoformat(f["collected_at"])
            price_val = Decimal(f["price"])
            base_price_val = Decimal(f["base_price_brl"])

            # Merge updates the existing record if primary key (id) matches,
            # otherwise it inserts a new record.
            flight_model = FlightModel(
                id=f["id"],
                airline=f["airline"],
                origin=f["origin"],
                destination=f["destination"],
                departure_date=dep_date,
                arrival_date=arr_date,
                price=price_val,
                currency=f["currency"],
                base_price_brl=base_price_val,
                duration=int(f["duration"]),
                stops=int(f["stops"]),
                cabin_class=f["cabin_class"],
                booking_url=f["booking_url"],
                collected_at=coll_date
            )
            await session.merge(flight_model)
            
            # Record price history point
            history = FlightPriceHistoryModel(
                flight_id=f["id"],
                price=price_val,
                currency=f["currency"],
                recorded_at=coll_date
            )
            session.add(history)
            
        await session.commit()
        logger.info(f"Saved {len(flights_data)} flights to DB.")

@dramatiq.actor(max_retries=3)
def save_flights_task(flights_data: List[dict]):
    """Background worker task to save collected flights to PostgreSQL."""
    logger.info("Executing background task to save flights.")
    asyncio.run(save_flights_async(flights_data))

@dramatiq.actor(max_retries=2)
def scrape_and_cache_flights_task(origin: str, destination: str, departure_date_str: str, collector_name: str, strategy: str):
    """
    Background worker task that spawns a subprocess to scrape flights.
    Spawning a separate process runs on its own main thread, avoiding
    Windows asyncio/Playwright subprocess issues inside background worker threads.
    """
    import subprocess
    import sys
    import os
    
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "run_scraper.py")
    python_exe = sys.executable
    
    logger.info(f"Dramatiq worker delegating scrape for {collector_name} ({origin}->{destination}) to external process...")
    
    # Run the scraper script as a subprocess synchronously
    result = subprocess.run([
        python_exe,
        script_path,
        origin,
        destination,
        departure_date_str,
        collector_name,
        strategy
    ], capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        logger.info(f"Dramatiq worker successfully finished scrape process for {collector_name}")
    else:
        logger.error(f"Dramatiq worker scraper process failed for {collector_name} with exit code {result.returncode}")
        if result.stderr:
            logger.error(f"Subprocess stderr: {result.stderr.strip()}")

@dramatiq.actor(max_retries=1)
def update_hotels_task(city_code: str):
    """
    Background worker task that spawns a subprocess to scrape hotels for a given city
    using populate_hotels.py script to avoid Playwright async context issues.
    """
    import subprocess
    import sys
    import os
    
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "populate_hotels.py")
    python_exe = sys.executable
    
    logger.info(f"Dramatiq worker delegating hotel scrape for city {city_code} to external process...")
    
    # Run the scraper script as a subprocess synchronously
    result = subprocess.run([
        python_exe,
        script_path,
        "--city",
        city_code
    ], capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        logger.info(f"Dramatiq worker successfully finished hotel scrape process for {city_code}")
    else:
        logger.error(f"Dramatiq worker hotel scraper process failed for {city_code} with exit code {result.returncode}")
        if result.stderr:
            logger.error(f"Subprocess stderr: {result.stderr.strip()}")


