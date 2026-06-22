from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import json
import time
from loguru import logger
from services.accommodation_service import accommodation_service
from telemetry.setup import (
    search_duration_seconds,
    hotels_returned_total,
    pousadas_returned_total,
    hostels_returned_total,
    resorts_returned_total,
    search_errors_total,
)

router = APIRouter(prefix="/api/hotels", tags=["hotels"])


@router.get("")
async def search_hotels(
    destination: str,
    checkin: str,
    checkout: str,
    adults: int = 1,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    rating: Optional[float] = None,
    stars: Optional[str] = Query(None, description="Comma-separated stars, e.g., '3,4,5'"),
    amenities: Optional[str] = Query(None, description="Comma-separated amenities, e.g., 'Wi-Fi,Piscina'"),
    types: Optional[str] = Query(None, description="Comma-separated lodging types, e.g., 'hotel,pousada'"),
    bounds: Optional[str] = Query(None, description="JSON string or comma-separated NE_lat,NE_lon,SW_lat,SW_lon"),
    polygon: Optional[str] = Query(None, description="JSON list of coordinates, e.g. '[[lat1,lon1],[lat2,lon2],...]'"),
):
    start_time = time.time()
    try:
        # Parse lists
        stars_list = [int(s.strip()) for s in stars.split(",") if s.strip()] if stars else None
        amenities_list = [a.strip() for a in amenities.split(",") if a.strip()] if amenities else None
        types_list = [t.strip().lower() for t in types.split(",") if t.strip()] if types else None

        # Parse bounds
        bounds_dict = None
        if bounds:
            try:
                bounds_dict = json.loads(bounds)
            except Exception:
                parts = [float(p.strip()) for p in bounds.split(",") if p.strip()]
                if len(parts) == 4:
                    bounds_dict = {"north": parts[0], "east": parts[1], "south": parts[2], "west": parts[3]}

        # Parse polygon
        polygon_list = None
        if polygon:
            try:
                polygon_list = json.loads(polygon)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid polygon JSON: {e}")

        results = await accommodation_service.search_accommodations(
            city=destination.upper(),
            checkin_date=checkin,
            checkout_date=checkout,
            min_price=min_price,
            max_price=max_price,
            rating=rating,
            stars=stars_list,
            amenities=amenities_list,
            types=types_list,
            bounds=bounds_dict,
            polygon=polygon_list,
        )

        # Track metrics
        duration = time.time() - start_time
        search_duration_seconds.observe(duration)

        counts = {"hotel": 0, "pousada": 0, "hostel": 0, "resort": 0}
        for item in results:
            t = item.get("type", "").lower()
            if t in counts:
                counts[t] += 1

        hotels_returned_total.inc(counts["hotel"])
        pousadas_returned_total.inc(counts["pousada"])
        hostels_returned_total.inc(counts["hostel"])
        resorts_returned_total.inc(counts["resort"])

        logger.info(
            f"Hotel search completed. Destination: {destination.upper()}, Duration: {duration:.3f}s. "
            f"Results: {len(results)} (Hotels: {counts['hotel']}, Pousadas: {counts['pousada']}, "
            f"Hostels: {counts['hostel']}, Resorts: {counts['resort']})"
        )

        return results
    except Exception as e:
        search_errors_total.inc()
        logger.error(f"Error searching hotels for {destination}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
