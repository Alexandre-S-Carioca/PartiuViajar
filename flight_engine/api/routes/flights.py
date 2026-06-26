from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import time
from application.dto.flight_dto import SearchFlightRequest, FlightDTO
from application.queries.search_flights import search_flights_query_handler
from telemetry.setup import search_duration_seconds, requests_total, search_errors_total
from core.security import verify_token, limiter

router = APIRouter(prefix="/api/v1/flights", tags=["flights"])

@router.get("/search", response_model=List[FlightDTO])
@limiter.limit("5/minute")
async def search_flights(
    request: Request,
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
    strategy: str = "cheapest",
    username: str = Depends(verify_token)
):
    requests_total.inc()
    start_time = time.time()
    
    req = SearchFlightRequest(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        adults=adults,
        strategy=strategy
    )
    
    try:
        results = await search_flights_query_handler.handle(req)
        search_duration_seconds.observe(time.time() - start_time)
        return results
    except Exception as e:
        search_errors_total.inc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse

@router.get("/stream")
@limiter.limit("5/minute")
async def stream_flights(
    request: Request,
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
    strategy: str = "cheapest",
    username: str = Depends(verify_token)
):
    req = SearchFlightRequest(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        adults=adults,
        strategy=strategy
    )
    
    # Needs to import search_service here if not imported at top
    from services.search_service import search_service
    return StreamingResponse(search_service.stream_search(req), media_type="text/event-stream")

from infrastructure.clients.aviationstack_client import aviationstack_client
from application.dto.flight_status_dto import FlightStatusDTO

@router.get("/live/{flight_iata}", response_model=FlightStatusDTO)
@limiter.limit("5/minute")
async def get_live_flight_status(request: Request, flight_iata: str):
    """
    Returns the real-time status of a flight using its IATA code.
    Example: 3U9619
    """
    flight_data = await aviationstack_client.get_live_flight_status(flight_iata)
    if not flight_data:
        raise HTTPException(status_code=404, detail="Flight not found or live status unavailable")
    return FlightStatusDTO.from_api_response(flight_data)

from infrastructure.collectors.opensky_collector import OpenSkyCollector
opensky_collector = OpenSkyCollector()

@router.get("/live-radar")
async def get_live_radar(lamin: float, lamax: float, lomin: float, lomax: float):
    """
    Returns live flights in a bounding box using OpenSky Network.
    """
    return await opensky_collector.fetch_live_flights(lamin, lamax, lomin, lomax)


