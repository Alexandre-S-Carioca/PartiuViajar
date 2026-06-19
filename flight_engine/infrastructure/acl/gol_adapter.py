from typing import Any
from domain.entities import Flight
from decimal import Decimal
from datetime import datetime
from services.currency_service import currency_service

class GolAdapter:
    @staticmethod
    def normalize(data: dict) -> Flight:
        """
        Adapts GOL's external response format to our internal Flight domain entity.
        GOL uses {"price": "520"}.
        """
        return Flight(
            airline="GOL",
            origin=data.get("origin_airport", "N/A"),
            destination=data.get("destination_airport", "N/A"),
            departure_date=datetime.fromisoformat(data.get("departure", datetime.utcnow().isoformat())),
            arrival_date=datetime.fromisoformat(data.get("arrival", datetime.utcnow().isoformat())),
            price=Decimal(data.get("price", 0)),
            currency=data.get("currency_code", "BRL"),
            base_price_brl=currency_service.to_brl(Decimal(data.get("price", 0)), data.get("currency_code", "BRL")),
            duration=data.get("duration", 0),
            stops=data.get("stops", 0),
            cabin_class=data.get("cabin", "ECONOMY"),
            booking_url=f"https://www.voegol.com.br/mock/booking?id={data.get('id', '')}"
        )
