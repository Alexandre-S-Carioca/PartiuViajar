from typing import Any
from domain.entities import Flight
from decimal import Decimal
from datetime import datetime
from services.currency_service import currency_service

class LatamAdapter:
    @staticmethod
    def normalize(data: dict) -> Flight:
        """
        Adapts LATAM's external response format to our internal Flight domain entity.
        LATAM uses {"fare": "520"} instead of "price".
        """
        return Flight(
            airline="LATAM",
            origin=data.get("origin", "N/A"),
            destination=data.get("destination", "N/A"),
            departure_date=datetime.fromisoformat(data.get("departure_time", datetime.utcnow().isoformat())),
            arrival_date=datetime.fromisoformat(data.get("arrival_time", datetime.utcnow().isoformat())),
            price=Decimal(data.get("fare", 0)),
            currency=data.get("currency", "BRL"),
            base_price_brl=currency_service.to_brl(Decimal(data.get("fare", 0)), data.get("currency", "BRL")),
            duration=data.get("duration_minutes", 0),
            stops=data.get("stops", 0),
            cabin_class=data.get("class", "ECONOMY"),
            booking_url=f"https://www.latamairlines.com/mock/booking?id={data.get('flight_id', '')}"
        )
