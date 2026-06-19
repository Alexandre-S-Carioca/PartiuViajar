from typing import Any
from domain.entities import Flight
from decimal import Decimal
from datetime import datetime
from services.currency_service import currency_service

class CopaAdapter:
    @staticmethod
    def normalize(data: dict) -> Flight:
        return Flight(
            airline="COPA",
            origin=data.get("origin", "N/A"),
            destination=data.get("destination", "N/A"),
            departure_date=datetime.fromisoformat(data.get("departure_datetime", datetime.utcnow().isoformat())),
            arrival_date=datetime.fromisoformat(data.get("arrival_datetime", datetime.utcnow().isoformat())),
            price=Decimal(data.get("price", 0)),
            currency=data.get("currency", "USD"),
            base_price_brl=currency_service.to_brl(Decimal(data.get("price", 0)), data.get("currency", "USD")),
            duration=data.get("duration", 0),
            stops=data.get("stops", 0),
            cabin_class=data.get("cabin", "ECONOMY"),
            booking_url=f"https://www.copaair.com/mock/booking?id={data.get('flight_id', '')}"
        )
