from typing import List
from datetime import datetime
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.acl.gol_adapter import GolAdapter
from domain.entities import Flight
from core.feature_flags import feature_flags
import logging

logger = logging.getLogger(__name__)

class GolCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="GOL")
        self.base_url = "https://api.gol.mock/v1/flights"

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int
    ) -> List[Flight]:
        if not feature_flags.ENABLE_GOL:
            logger.info(f"[{self.name}] Collector disabled via feature flag.")
            return []

        try:
            params = {
                "origin": origin,
                "dest": destination,
                "dep_date": departure_date.strftime("%Y-%m-%d"),
                "adt": adults
            }
            # Simulate external API call
            
            response_data = {
                "data": [
                    {
                        "id": "GOL456",
                        "origin_airport": origin,
                        "destination_airport": destination,
                        "departure": departure_date.isoformat(),
                        "arrival": departure_date.isoformat(),
                        "price": "490.00",
                        "currency_code": "BRL",
                        "duration": 115,
                        "stops": 0,
                        "cabin": "ECONOMY"
                    }
                ]
            }

            flights = [GolAdapter.normalize(f) for f in response_data.get("data", [])]
            return flights
        except Exception as e:
            logger.error(f"[{self.name}] Error fetching flights: {e}")
            return []
