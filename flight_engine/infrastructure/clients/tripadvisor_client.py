import logging
import httpx
import time
from typing import List, Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)

TRIPADVISOR_HOST = "tripadvisor16.p.rapidapi.com"
BASE_URL = f"https://{TRIPADVISOR_HOST}/api/v1/restaurant"


class TripAdvisorClient:
    """Client para a API TripAdvisor via RapidAPI."""

    def __init__(self):
        self.headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": TRIPADVISOR_HOST,
        }
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 3600  # 1 hora — restaurantes mudam pouco

    def _cached(self, key: str) -> Optional[List]:
        entry = self._cache.get(key)
        if entry and (time.time() - entry["ts"]) < self._cache_ttl:
            logger.info(f"[TripAdvisor] Cache hit: {key}")
            return entry["data"]
        return None

    def _store(self, key: str, data: List):
        self._cache[key] = {"data": data, "ts": time.time()}

    async def search_by_location_id(self, location_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca restaurantes por locationId do TripAdvisor."""
        cache_key = f"loc:{location_id}:{limit}"
        cached = self._cached(cache_key)
        if cached is not None:
            return cached

        url = f"{BASE_URL}/searchRestaurants"
        params = {"locationId": location_id}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self.headers, params=params)
                logger.info(f"[TripAdvisor] searchRestaurants locationId={location_id} → HTTP {resp.status_code}")

                if resp.status_code == 200:
                    body = resp.json()
                    raw_list = body.get("data", {}).get("data", [])
                    restaurants = [self._normalize(r) for r in raw_list[:limit] if r.get("name")]
                    self._store(cache_key, restaurants)
                    return restaurants

                elif resp.status_code == 403:
                    logger.error("[TripAdvisor] 403 Forbidden — verifique se a chave está subscrita na API tripadvisor16 no RapidAPI.")
                elif resp.status_code == 429:
                    logger.warning("[TripAdvisor] Rate limit atingido (429).")
                else:
                    logger.error(f"[TripAdvisor] Erro HTTP {resp.status_code}: {resp.text[:200]}")

        except Exception as e:
            logger.error(f"[TripAdvisor] Falha na requisição: {e}")

        return []

    async def search_by_geo(self, lat: float, lon: float, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca restaurantes próximos a coordenadas geográficas."""
        cache_key = f"geo:{round(lat,2)}:{round(lon,2)}:{limit}"
        cached = self._cached(cache_key)
        if cached is not None:
            return cached

        url = f"{BASE_URL}/searchRestaurants"
        params = {"latitude": lat, "longitude": lon}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self.headers, params=params)
                logger.info(f"[TripAdvisor] searchRestaurants lat={lat},lon={lon} → HTTP {resp.status_code}")

                if resp.status_code == 200:
                    body = resp.json()
                    raw_list = body.get("data", {}).get("data", [])
                    restaurants = [self._normalize(r) for r in raw_list[:limit] if r.get("name")]
                    self._store(cache_key, restaurants)
                    return restaurants

                elif resp.status_code == 403:
                    logger.error("[TripAdvisor] 403 Forbidden — chave sem acesso à API.")
                elif resp.status_code == 429:
                    logger.warning("[TripAdvisor] Rate limit atingido (429).")
                else:
                    logger.error(f"[TripAdvisor] Erro HTTP {resp.status_code}: {resp.text[:200]}")

        except Exception as e:
            logger.error(f"[TripAdvisor] Falha na requisição: {e}")

        return []

    def _normalize(self, raw: Dict) -> Dict[str, Any]:
        """Normaliza um item da API para o formato interno."""
        photo = None
        photos = raw.get("photos") or raw.get("heroImgUrl")
        if isinstance(photos, list) and photos:
            photo = photos[0].get("src") or photos[0].get("url")
        elif isinstance(photos, str):
            photo = photos

        location = raw.get("establishmentTypeAndCuisineTags") or []
        cuisines = ", ".join(location[:2]) if location else "Restaurante"

        return {
            "location_id": raw.get("locationId") or raw.get("id"),
            "name": raw.get("name", ""),
            "rating": raw.get("averageRating") or raw.get("rating"),
            "reviews": raw.get("userReviewCount") or raw.get("reviewCount", 0),
            "price_level": raw.get("priceTag") or raw.get("priceLevel", ""),
            "cuisines": cuisines,
            "address": raw.get("address") or raw.get("addressObj", {}).get("street1", ""),
            "latitude": raw.get("latitude"),
            "longitude": raw.get("longitude"),
            "photo": photo,
            "url": f"https://www.tripadvisor.com.br/Restaurant_Review-d{raw.get('locationId', '')}.html",
        }


tripadvisor_client = TripAdvisorClient()
