from typing import Any
from domain.entities import Flight
from decimal import Decimal
from datetime import datetime
from services.currency_service import currency_service

class AzulAdapter:
    @staticmethod
    def normalize(data: dict) -> Flight:
        return Flight(
            airline="AZUL",
            origin=data.get("from", "N/A"),
            destination=data.get("to", "N/A"),
            departure_date=datetime.fromisoformat(data.get("dep", datetime.utcnow().isoformat())),
            arrival_date=datetime.fromisoformat(data.get("arr", datetime.utcnow().isoformat())),
            price=Decimal(data.get("total_amount", 0)),
            currency=data.get("curr", "BRL"),
            base_price_brl=currency_service.to_brl(Decimal(data.get("total_amount", 0)), data.get("curr", "BRL")),
            duration=data.get("time_mins", 0),
            stops=data.get("connections", 0),
            cabin_class=data.get("class_type", "ECONOMY"),
            booking_url=f"https://www.voeazul.com.br/mock/booking?id={data.get('flightId', '')}"
        )
