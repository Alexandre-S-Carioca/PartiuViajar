import urllib.parse
from typing import Optional, Dict, Any
from core.config import settings
from factories.http_client_factory import HttpClientFactory
import pybreaker
from aiolimiter import AsyncLimiter
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class AviationstackClient:
    def __init__(self):
        self.base_url = "http://api.aviationstack.com/v1"
        self.api_key = settings.AVIATIONSTACK_API_KEY
        self.limiter = AsyncLimiter(settings.RATE_LIMIT_RPS, 1)
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=settings.CB_FAIL_MAX,
            reset_timeout=settings.CB_RESET_TIMEOUT
        )

    async def get_live_flight_status(self, flight_iata: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the live status of a flight by its IATA code (e.g., '3U9619').
        Returns the raw flight data dictionary if found, otherwise None.
        """
        if not self.api_key:
            logger.error("Aviationstack API key is not configured.")
            return None

        # Endpoint requires HTTP due to free tier restrictions
        url = f"{self.base_url}/flights"
        # Se começa com 3 letras (ex: AZU4712), é ICAO. Se 2 letras (ex: AD4712), é IATA.
        import re
        is_icao = bool(re.match(r'^[a-zA-Z]{3}\d+', flight_iata))
        
        params = {
            "access_key": self.api_key,
            "flight_icao" if is_icao else "flight_iata": flight_iata,
            "limit": 1
        }

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            reraise=True
        )
        async def _do_get():
            async with self.limiter:
                client = HttpClientFactory.get_client()
                logger.info(f"Fetching live status for flight {flight_iata}")
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        try:
            data = await _do_get()
            flights = data.get("data", [])
            if flights:
                return flights[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching flight status for {flight_iata}: {str(e)}")
            return None

aviationstack_client = AviationstackClient()
