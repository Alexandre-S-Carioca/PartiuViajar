from typing import Any
from domain.entities import Flight
from decimal import Decimal
from datetime import datetime
from services.currency_service import currency_service

class TapAdapter:
    @staticmethod
    def normalize(data: dict) -> Flight:
        return Flight(
            airline="TAP",
            origin=data.get("from", "N/A"),
            destination=data.get("to", "N/A"),
            departure_date=datetime.fromisoformat(data.get("departure", datetime.utcnow().isoformat())),
            arrival_date=datetime.fromisoformat(data.get("arrival", datetime.utcnow().isoformat())),
            price=Decimal(data.get("price_eur", 0)),
            currency="EUR",
            base_price_brl=currency_service.to_brl(Decimal(data.get("price_eur", 0)), "EUR"),
            duration=data.get("time", 0),
            stops=data.get("stops", 0),
            cabin_class=data.get("cabin", "ECONOMY"),
            booking_url=f"https://www.flytap.com/mock/booking?id={data.get('id', '')}"
        )
