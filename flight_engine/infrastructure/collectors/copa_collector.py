from typing import List
from datetime import datetime
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.acl.copa_adapter import CopaAdapter
from domain.entities import Flight
from core.feature_flags import feature_flags
import logging

logger = logging.getLogger(__name__)

class CopaCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="COPA")

    async def fetch_flights(self, origin: str, destination: str, departure_date: datetime, adults: int) -> List[Flight]:
        if not feature_flags.ENABLE_COPA:
            return []
        try:
            response_data = {
                "flights": [{
                    "flight_id": "CM111", "origin": origin, "destination": destination,
                    "departure_datetime": departure_date.isoformat(), "arrival_datetime": departure_date.isoformat(),
                    "price": "500.00", "currency": "USD", "duration": 300, "stops": 1, "cabin": "ECONOMY"
                }]
            }
            return [CopaAdapter.normalize(f) for f in response_data.get("flights", [])]
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return []
