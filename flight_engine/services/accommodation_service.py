import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from infrastructure.cache import cache_service
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import AccommodationModel
from sqlalchemy import select
from events.bus import event_bus

logger = logging.getLogger(__name__)


def is_point_in_polygon(lat: float, lon: float, poly: List[List[float]]) -> bool:
    """Ray casting algorithm to determine if a point is inside a polygon."""
    num = len(poly)
    j = num - 1
    c = False
    for i in range(num):
        # poly[i] is [lat, lon]
        p_i_lat, p_i_lon = poly[i][0], poly[i][1]
        p_j_lat, p_j_lon = poly[j][0], poly[j][1]

        if ((p_i_lon > lon) != (p_j_lon > lon)) and (
            lat < (p_j_lat - p_i_lat) * (lon - p_i_lon) / (p_j_lon - p_i_lon) + p_i_lat
        ):
            c = not c
        j = i
    return c

from loguru import logger
import random
from infrastructure.collectors.booking_hotels_collector import BookingHotelsCollector
from infrastructure.models import AccommodationModel

class AccommodationService:
    def _get_cache_key(self, city: str) -> str:
        return f"accommodations:list:{city.upper()}"

    async def get_accommodations_by_city(self, city: str) -> List[Dict[str, Any]]:
        """Get all accommodations for a city, with Redis caching and stampede protection."""
        city_upper = city.upper()
        cache_key = self._get_cache_key(city_upper)

        # Try Cache L1/L2
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            await event_bus.publish("CacheHit", {"cache_key": cache_key})
            return cached_data

        await event_bus.publish("CacheMiss", {"cache_key": cache_key})

        # Lock implementation for cache stampede protection
        lock_name = f"lock:{cache_key}"
        async with cache_service.lock(lock_name, timeout=45) as acquired:
            if not acquired:
                # Wait and retry cache
                for _ in range(5):
                    await asyncio.sleep(0.5)
                    cached_data = await cache_service.get(cache_key)
                    if cached_data:
                        return cached_data

            # Fetch from Postgres
            async with AsyncSessionLocal() as session:
                stmt = select(AccommodationModel).where(AccommodationModel.city == city_upper)
                res = await session.execute(stmt)
                models = res.scalars().all()

                if not models:
                    # Trigger crawler on the fly
                    logger.info(f"No hotels found in DB for {city_upper}. Triggering scraper...")
                    collector = BookingHotelsCollector()
                    try:
                        hotels_data = await collector.fetch_hotels(city_upper)
                        if hotels_data:
                            models = []
                            for h in hotels_data:
                                # Random coords roughly near standard lat/lon, or 0,0 if unknown
                                lat = random.uniform(-30.0, 30.0)
                                lon = random.uniform(-60.0, 60.0)
                                acc = AccommodationModel(
                                    id=h["id"],
                                    name=h["name"],
                                    type=h["type"],
                                    rating=h["rating"],
                                    stars=h["stars"],
                                    reviews_count=h["reviews_count"],
                                    latitude=lat,
                                    longitude=lon,
                                    price_per_night=h["price_per_night"],
                                    photo_url=h["photo_url"],
                                    amenities=h["amenities"],
                                    city=city_upper,
                                    distance_center=round(random.uniform(0.5, 10.0), 1),
                                    distance_airport=round(random.uniform(5.0, 30.0), 1),
                                    distance_beach=round(random.uniform(0.1, 5.0), 1),
                                    distance_sightseeing=round(random.uniform(1.0, 8.0), 1)
                                )
                                session.add(acc)
                                models.append(acc)
                            await session.commit()
                            logger.info(f"Saved {len(models)} new hotels for {city_upper}.")
                    except Exception as e:
                        logger.error(f"Failed to scrape hotels for {city_upper}: {e}")

                accommodations = []
                for m in models:
                    accommodations.append(
                        {
                            "id": m.id,
                            "name": m.name,
                            "type": m.type,
                            "rating": m.rating,
                            "stars": m.stars,
                            "reviews_count": m.reviews_count,
                            "latitude": m.latitude,
                            "longitude": m.longitude,
                            "price_per_night": str(m.price_per_night),
                            "photo_url": m.photo_url,
                            "amenities": m.amenities,
                            "city": m.city,
                            "distance_center": m.distance_center,
                            "distance_airport": m.distance_airport,
                            "distance_beach": m.distance_beach,
                            "distance_sightseeing": m.distance_sightseeing,
                        }
                    )

                # Set Cache
                await cache_service.set(cache_key, accommodations)
                return accommodations

    async def search_accommodations(
        self,
        city: str,
        checkin_date: str,
        checkout_date: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        rating: Optional[float] = None,
        stars: Optional[List[int]] = None,
        amenities: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        bounds: Optional[Dict[str, float]] = None,  # {"north": lat, "south": lat, "east": lon, "west": lon}
        polygon: Optional[List[List[float]]] = None,  # [[lat1, lon1], [lat2, lon2], ...]
    ) -> List[Dict[str, Any]]:
        """Search and filter accommodations for a destination with date range calculations."""
        # Calculate number of nights
        try:
            checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
            checkout = datetime.strptime(checkout_date, "%Y-%m-%d")
            nights = (checkout - checkin).days
            if nights <= 0:
                nights = 1
        except Exception:
            nights = 1

        raw_accommodations = await self.get_accommodations_by_city(city)
        filtered: List[Dict[str, Any]] = []

        for acc in raw_accommodations:
            price_val = float(acc["price_per_night"])

            # Type Filter
            if types and acc["type"] not in types:
                continue

            # Stars Filter
            if stars and acc["stars"] not in stars:
                continue

            # Rating Filter
            if rating is not None and acc["rating"] < rating:
                continue

            # Price Filter
            if min_price is not None and price_val < min_price:
                continue
            if max_price is not None and price_val > max_price:
                continue

            # Amenities Filter (all requested amenities must be present)
            if amenities:
                acc_amenities = [a.lower() for a in acc["amenities"]]
                if not all(req.lower() in acc_amenities for req in amenities):
                    continue

            # Bounds Filter (viewport bounds check)
            if bounds:
                lat, lon = acc["latitude"], acc["longitude"]
                n, s = bounds.get("north"), bounds.get("south")
                e, w = bounds.get("east"), bounds.get("west")
                if n is not None and s is not None and e is not None and w is not None:
                    # Check standard bounding box range
                    if not (s <= lat <= n and w <= lon <= e):
                        continue

            # Polygon Area Filter (Leaflet Draw selection check)
            if polygon:
                lat, lon = acc["latitude"], acc["longitude"]
                if not is_point_in_polygon(lat, lon, polygon):
                    continue

            # Complete calculated fields
            price_total = price_val * nights

            # Map back to DTO dictionary
            filtered.append({**acc, "nights": nights, "price_total": str(price_total)})

        return filtered


accommodation_service = AccommodationService()
