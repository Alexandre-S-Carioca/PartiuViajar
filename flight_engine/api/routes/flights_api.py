from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import time
from application.dto.flight_dto import SearchFlightRequest
from application.queries.search_flights import search_flights_query_handler
from telemetry.setup import search_duration_seconds, requests_total, search_errors_total
from core.security import limiter
from services.search_service import search_service

router = APIRouter(prefix="/api/flights", tags=["flights_api"])


@router.get("")
@limiter.limit("10/minute")
async def search_flights(
    request: Request, origin: str, destination: str, departure_date: str, adults: int = 1, strategy: str = "cheapest"
):
    requests_total.inc()
    start_time = time.time()

    req = SearchFlightRequest(
        origin=origin, destination=destination, departure_date=departure_date, adults=adults, strategy=strategy
    )

    try:
        results = await search_flights_query_handler.handle(req)
        search_duration_seconds.observe(time.time() - start_time)
        return results
    except Exception as e:
        search_errors_total.inc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
@limiter.limit("10/minute")
async def stream_flights(
    request: Request, origin: str, destination: str, departure_date: str, adults: int = 1, strategy: str = "cheapest"
):
    req = SearchFlightRequest(
        origin=origin, destination=destination, departure_date=departure_date, adults=adults, strategy=strategy
    )
    return StreamingResponse(search_service.stream_search(req), media_type="text/event-stream")
