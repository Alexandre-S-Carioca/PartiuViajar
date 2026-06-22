from fastapi import APIRouter, HTTPException
from typing import Optional
import json
from services.accommodation_service import accommodation_service

router = APIRouter(prefix="/api/map", tags=["map"])


def get_marker_color(price: float) -> str:
    """Determine marker color based on price range."""
    if price <= 150.0:
        return "green"
    elif price <= 250.0:
        return "yellow"
    elif price <= 400.0:
        return "orange"
    else:
        return "red"


@router.get("")
async def get_map_data(
    destination: str,
    checkin: str,
    checkout: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    rating: Optional[float] = None,
    stars: Optional[str] = None,
    amenities: Optional[str] = None,
    types: Optional[str] = None,
    bounds: Optional[str] = None,
    polygon: Optional[str] = None,
):
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
            except Exception:
                pass

        accommodations = await accommodation_service.search_accommodations(
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

        markers = []
        heatmap = []
        for acc in accommodations:
            price_val = float(acc["price_per_night"])
            color = get_marker_color(price_val)

            markers.append(
                {
                    "id": acc["id"],
                    "name": acc["name"],
                    "type": acc["type"],
                    "latitude": acc["latitude"],
                    "longitude": acc["longitude"],
                    "rating": acc["rating"],
                    "stars": acc["stars"],
                    "price_per_night": price_val,
                    "price_total": float(acc["price_total"]),
                    "nights": acc["nights"],
                    "photo_url": acc["photo_url"],
                    "amenities": acc["amenities"],
                    "distance_center": acc["distance_center"],
                    "marker_color": color,
                }
            )

            # Heatmap point: [lat, lon, intensity].
            # We can use price as intensity, normalized or raw.
            # Leaflet Heatmap expects [lat, lon, intensity]. Let's pass price_per_night as intensity.
            heatmap.append([acc["latitude"], acc["longitude"], price_val])

        return {"markers": markers, "heatmap": heatmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
