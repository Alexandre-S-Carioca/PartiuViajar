import logging
import httpx
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class OpenSkyCollector:
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.name = "OpenSky"
        self.auth = (username, password) if username and password else None
        self.base_url = "https://opensky-network.org/api/states/all"
        self._cache: Dict[str, Any] = {}  # cache: bbox_key -> {data, timestamp}
        self._cache_ttl = 15  # segundos

    async def fetch_live_flights(self, lamin: float, lamax: float, lomin: float, lomax: float) -> List[Dict[str, Any]]:
        """
        Fetch live flights within a bounding box.
        Cache de 15s para respeitar o rate limit anônimo da OpenSky.
        """
        # Cache key arredondado para 1 casa decimal para agrupar bboxes próximas
        cache_key = f"{round(lamin,1)},{round(lamax,1)},{round(lomin,1)},{round(lomax,1)}"
        now = time.time()
        cached = self._cache.get(cache_key)
        if cached and (now - cached['ts']) < self._cache_ttl:
            logger.info(f"[{self.name}] Cache hit para bbox {cache_key}")
            return cached['data']

        url = f"{self.base_url}?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
        
        flights = []
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"[{self.name}] Buscando voos ao vivo no radar (BBOX: {lamin},{lomin} -> {lamax},{lomax})")
                
                kwargs = {"timeout": 15.0}
                if self.auth:
                    # Note: OpenSky doesn't accept Basic Auth anymore as per new docs, they want OAuth2.
                    # But if an anonymous request works, we'll use that. 
                    # If the user has a Bearer token, we can inject it via headers.
                    # For now, we rely on the anonymous IP rate limit.
                    pass 

                resp = await client.get(url, **kwargs)
                
                if resp.status_code == 200:
                    data = resp.json()
                    states = data.get("states", [])
                    if states:
                        for s in states:
                            # State vector index reference:
                            # 0: icao24, 1: callsign, 2: origin_country, 5: longitude, 6: latitude, 
                            # 7: baro_altitude, 9: velocity, 10: true_track
                            if s[5] is not None and s[6] is not None:
                                flights.append({
                                    "icao24": s[0],
                                    "callsign": s[1].strip() if s[1] else "UNKNOWN",
                                    "origin_country": s[2],
                                    "longitude": s[5],
                                    "latitude": s[6],
                                    "altitude": s[7] or 0,
                                    "velocity": s[9] or 0,  # m/s
                                    "true_track": s[10] or 0  # degrees
                                })
                elif resp.status_code == 429:
                    logger.warning(f"[{self.name}] Rate limit exceeded. Retornando cache se disponível.")
                    if cached:
                        return cached['data']
                else:
                    logger.error(f"[{self.name}] Erro OpenSky: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"[{self.name}] Falha na coleta do radar: {e}")
            if cached:
                return cached['data']

        # Salva no cache apenas se tiver dados
        if flights:
            self._cache[cache_key] = {'data': flights, 'ts': now}

        return flights
