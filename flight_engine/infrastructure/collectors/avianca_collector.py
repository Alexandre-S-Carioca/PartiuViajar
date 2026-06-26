from typing import List
from datetime import datetime
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.acl.avianca_adapter import AviancaAdapter
from domain.entities import Flight
from core.feature_flags import feature_flags
import logging

logger = logging.getLogger(__name__)

class AviancaCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="AVIANCA")

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int, currency: str = "BRL"
    ) -> List[Flight]:
        if not feature_flags.ENABLE_AVIANCA:
            return []
        try:
            response_data = {
                "flights": [{
                    "id": "AV222", "origin": origin, "destination": destination,
                    "dep": departure_date.isoformat(), "arr": departure_date.isoformat(),
                    "cost": "150000.00", "currency": "COP", "duration_mins": 200, "connections": 0, "class": "ECONOMY"
                }]
            }
            return [AviancaAdapter.normalize(f) for f in response_data.get("flights", [])]
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return []
