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
