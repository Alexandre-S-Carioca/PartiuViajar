import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from contextlib import asynccontextmanager

from core.config import settings
from application.dto.flight_dto import SearchFlightRequest, FlightDTO
from application.queries.search_flights import search_flights_query_handler
from infrastructure.registry import registry
from infrastructure.collectors.latam_collector import LatamCollector
from infrastructure.collectors.gol_collector import GolCollector
from infrastructure.collectors.azul_collector import AzulCollector
from infrastructure.collectors.copa_collector import CopaCollector
from infrastructure.collectors.avianca_collector import AviancaCollector
from infrastructure.collectors.tap_collector import TapCollector
from factories.http_client_factory import HttpClientFactory
from events.handlers import register_handlers
from jobs.scheduler import setup_scheduler
from api.routes import flights, health, auth, airports, price_history, alerts, hotels, travel, map, history, favorites, flights_api, restaurants
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.security import limiter
import logging
import sys

# Configure Loguru/Logging JSON
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    
    # Initialize Database Tables
    from infrastructure.db import engine, Base
    import infrastructure.models # Ensure models are imported
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Register Collectors
    # registry.register(LatamCollector())
    # registry.register(GolCollector())
    # registry.register(AzulCollector())
    # registry.register(CopaCollector())
    # registry.register(AviancaCollector())
    # registry.register(TapCollector())

    from infrastructure.collectors.google_flights_collector import GoogleFlightsCollector
    from infrastructure.collectors.kayak_collector import KayakCollector
    from infrastructure.collectors.gol_scrapestack_collector import GolScrapestackCollector
    
    registry.register(GoogleFlightsCollector())
    from infrastructure.collectors.google_flights_scrapestack_collector import GoogleFlightsScrapestackCollector
    registry.register(GoogleFlightsScrapestackCollector())
    registry.register(KayakCollector())
    registry.register(GolScrapestackCollector())

    # Register Events
    register_handlers()

    # Start Scheduler
    setup_scheduler()

    # Create HTTP Client session
    HttpClientFactory.get_client()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await HttpClientFactory.close()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(flights.router)
app.include_router(health.router)
app.include_router(airports.router)
app.include_router(price_history.router)
app.include_router(alerts.router)
app.include_router(hotels.router)
app.include_router(travel.router)
app.include_router(map.router)
app.include_router(history.router)
app.include_router(favorites.router)
app.include_router(flights_api.router)
app.include_router(restaurants.router)

import os
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static"))
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
