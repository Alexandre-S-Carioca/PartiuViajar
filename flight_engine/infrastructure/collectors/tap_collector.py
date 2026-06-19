from typing import List
from datetime import datetime
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.acl.tap_adapter import TapAdapter
from domain.entities import Flight
from core.feature_flags import feature_flags
import logging

logger = logging.getLogger(__name__)

class TapCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="TAP")

    async def fetch_flights(self, origin: str, destination: str, departure_date: datetime, adults: int) -> List[Flight]:
        if not feature_flags.ENABLE_TAP:
            return []
        try:
            response_data = {
                "flights": [{
                    "id": "TP333", "from": origin, "to": destination,
                    "departure": departure_date.isoformat(), "arrival": departure_date.isoformat(),
                    "price_eur": "250.00", "time": 400, "stops": 0, "cabin": "ECONOMY"
                }]
            }
            return [TapAdapter.normalize(f) for f in response_data.get("flights", [])]
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return []
