from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from core.security import check_anonymous_search_limit
import asyncio
import time
from datetime import datetime
from loguru import logger
from services.search_service import search_service
from services.accommodation_service import accommodation_service
from application.dto.flight_dto import SearchFlightRequest
from infrastructure.models import SearchHistoryModel
from infrastructure.db import AsyncSessionLocal
from telemetry.setup import (
    search_duration_seconds,
    flights_returned_total,
    hotels_returned_total,
    pousadas_returned_total,
    hostels_returned_total,
    resorts_returned_total,
    search_errors_total,
)

router = APIRouter(prefix="/api/travel", tags=["travel"])


async def save_search_history(
    origin: str, destination: str, dep_date_str: str, ret_date_str: Optional[str], adults: int
):
    """Save search query to search history table."""
    try:
        async with AsyncSessionLocal() as session:
            dep_date = datetime.strptime(dep_date_str, "%Y-%m-%d")
            ret_date = datetime.strptime(ret_date_str, "%Y-%m-%d") if ret_date_str else None

            history = SearchHistoryModel(
                origin=origin.upper(),
                destination=destination.upper(),
                departure_date=dep_date,
                return_date=ret_date,
                adults=adults,
            )
            session.add(history)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to save search history: {e}")


@router.get("")
async def unified_search(
    origin: str, destination: str, departure_date: str, return_date: Optional[str] = None, adults: int = 1,
    _: bool = Depends(check_anonymous_search_limit)
):
    start_time = time.time()
    # Log search in history asynchronously
    asyncio.create_task(save_search_history(origin, destination, departure_date, return_date, adults))

    # Prep flight requests
    outbound_req = SearchFlightRequest(
        origin=origin.upper(),
        destination=destination.upper(),
        departure_date=departure_date,
        adults=adults,
        strategy="cheapest",
    )

    inbound_req = None
    if return_date:
        inbound_req = SearchFlightRequest(
            origin=destination.upper(),
            destination=origin.upper(),
            departure_date=return_date,
            adults=adults,
            strategy="cheapest",
        )

    # Calculate checkin/checkout for hotels
    checkin_str = departure_date
    checkout_str = return_date if return_date else departure_date

    # Define tasks for asyncio.gather
    tasks = []

    # Task 0: Outbound flights
    tasks.append(search_service.search_v2(outbound_req))

    # Task 1: Inbound flights (if return_date provided)
    if inbound_req:
        tasks.append(search_service.search_v2(inbound_req))
    else:
        tasks.append(asyncio.sleep(0, result=[]))

    # Task 2: Accommodations
    tasks.append(
        accommodation_service.search_accommodations(
            city=destination.upper(), checkin_date=checkin_str, checkout_date=checkout_str
        )
    )

    try:
        # Run parallel searches
        outbound_flights, inbound_flights, hotels = await asyncio.gather(*tasks)

        # Serialize flights to DTO dict structures
        outbound_list = [
            {
                "id": f.id,
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
            }
            for f in outbound_flights
        ]

        inbound_list = [
            {
                "id": f.id,
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
            }
            for f in inbound_flights
        ]

        # Record metrics
        duration = time.time() - start_time
        search_duration_seconds.observe(duration)

        num_flights = len(outbound_list) + len(inbound_list)
        flights_returned_total.inc(num_flights)

        counts = {"hotel": 0, "pousada": 0, "hostel": 0, "resort": 0}
        for item in hotels:
            t = item.get("type", "").lower()
            if t in counts:
                counts[t] += 1

        hotels_returned_total.inc(counts["hotel"])
        pousadas_returned_total.inc(counts["pousada"])
        hostels_returned_total.inc(counts["hostel"])
        resorts_returned_total.inc(counts["resort"])

        logger.info(
            f"Unified travel search completed. {origin.upper()} -> {destination.upper()}, Duration: {duration:.3f}s. "
            f"Flights: {num_flights}, Accommodations: {len(hotels)} "
            f"(Hotels: {counts['hotel']}, Pousadas: {counts['pousada']}, "
            f"Hostels: {counts['hostel']}, Resorts: {counts['resort']})"
        )

        return {"flights": {"outbound": outbound_list, "inbound": inbound_list}, "accommodations": hotels}
    except Exception as e:
        search_errors_total.inc()
        logger.error(f"Error in unified search for {origin}->{destination}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
