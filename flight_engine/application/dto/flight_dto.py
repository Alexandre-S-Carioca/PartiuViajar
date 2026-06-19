from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class FlightDTO(BaseModel):
    id: str
    airline: str
    origin: str
    destination: str
    departure_date: datetime
    arrival_date: datetime
    price: Decimal
    currency: str
    base_price_brl: Decimal
    duration: int
    stops: int
    cabin_class: str
    booking_url: str
    collected_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SearchFlightRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str  # YYYY-MM-DD
    adults: int = 1
    strategy: str = "cheapest"
