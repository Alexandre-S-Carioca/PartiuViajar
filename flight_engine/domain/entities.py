from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import uuid


@dataclass(slots=True)
class Flight:
    airline: str
    origin: str
    destination: str
    departure_date: datetime
    arrival_date: datetime
    price: Decimal
    currency: str
    base_price_brl: Decimal
    duration: int  # in minutes
    stops: int
    cabin_class: str
    booking_url: str
    collected_at: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
