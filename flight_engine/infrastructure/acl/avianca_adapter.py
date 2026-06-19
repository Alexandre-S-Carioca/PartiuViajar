from typing import Any
from domain.entities import Flight
from decimal import Decimal
from datetime import datetime
from services.currency_service import currency_service

class AviancaAdapter:
    @staticmethod
    def normalize(data: dict) -> Flight:
        return Flight(
            airline="AVIANCA",
            origin=data.get("origin", "N/A"),
            destination=data.get("destination", "N/A"),
            departure_date=datetime.fromisoformat(data.get("dep", datetime.utcnow().isoformat())),
            arrival_date=datetime.fromisoformat(data.get("arr", datetime.utcnow().isoformat())),
            price=Decimal(data.get("cost", 0)),
            currency=data.get("currency", "COP"),
            base_price_brl=currency_service.to_brl(Decimal(data.get("cost", 0)), data.get("currency", "COP")),
            duration=data.get("duration_mins", 0),
            stops=data.get("connections", 0),
            cabin_class=data.get("class", "ECONOMY"),
            booking_url=f"https://www.avianca.com/mock/booking?id={data.get('id', '')}"
        )
