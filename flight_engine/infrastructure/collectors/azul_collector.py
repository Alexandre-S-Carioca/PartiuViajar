from typing import List
from datetime import datetime
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.acl.azul_adapter import AzulAdapter
from domain.entities import Flight
from core.feature_flags import feature_flags
import logging

logger = logging.getLogger(__name__)

class AzulCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="AZUL")
        self.base_url = "https://api.azul.mock/search"

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int, currency: str = "BRL"
    ) -> List[Flight]:
        if not feature_flags.ENABLE_AZUL:
            logger.info(f"[{self.name}] Collector disabled via feature flag.")
            return []

        try:
            response_data = {
                "flights": [
                    {
                        "flightId": "AZ789",
                        "from": origin,
                        "to": destination,
                        "dep": departure_date.isoformat(),
                        "arr": departure_date.isoformat(),
                        "total_amount": "550.00",
                        "curr": "BRL",
                        "time_mins": 130,
                        "connections": 0,
                        "class_type": "ECONOMY"
                    }
                ]
            }

            flights = [AzulAdapter.normalize(f) for f in response_data.get("flights", [])]
            return flights
        except Exception as e:
            logger.error(f"[{self.name}] Error fetching flights: {e}")
            return []
