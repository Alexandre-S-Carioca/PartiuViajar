from typing import List
from datetime import datetime
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.acl.latam_adapter import LatamAdapter
from domain.entities import Flight
from core.feature_flags import feature_flags
import logging

logger = logging.getLogger(__name__)

class LatamCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="LATAM")
        self.base_url = "https://api.latam.mock/flights"

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int
    ) -> List[Flight]:
        if not feature_flags.ENABLE_LATAM:
            logger.info(f"[{self.name}] Collector disabled via feature flag.")
            return []

        try:
            params = {
                "from": origin,
                "to": destination,
                "date": departure_date.strftime("%Y-%m-%d"),
                "passengers": adults
            }
            # Simulate external API call
            # response_data = await self._safe_get(self.base_url, params)
            
            # Mocking response for demonstration
            response_data = {
                "results": [
                    {
                        "flight_id": "LA123",
                        "origin": origin,
                        "destination": destination,
                        "departure_time": departure_date.isoformat(),
                        "arrival_time": departure_date.isoformat(),
                        "fare": "520.00",
                        "currency": "BRL",
                        "duration_minutes": 120,
                        "stops": 0,
                        "class": "ECONOMY"
                    }
                ]
            }

            flights = [LatamAdapter.normalize(flight_data) for flight_data in response_data.get("results", [])]
            return flights
        except Exception as e:
            logger.error(f"[{self.name}] Error fetching flights: {e}")
            return []
