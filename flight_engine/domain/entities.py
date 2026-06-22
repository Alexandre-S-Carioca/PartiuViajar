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
    id: str = None

    def __post_init__(self):
        if not self.id:
            import hashlib
            dep_str = self.departure_date.strftime("%Y-%m-%dT%H:%M")
            # Unique key for a specific flight route, schedule, and flight properties (airline, stops, duration)
            key = f"{self.airline}:{self.origin}:{self.destination}:{dep_str}:{self.duration}:{self.stops}".lower()
            self.id = hashlib.md5(key.encode()).hexdigest()


@dataclass(slots=True)
class Accommodation:
    name: str
    type: str  # 'hotel', 'pousada', 'hostel', 'resort'
    rating: float
    stars: int
    reviews_count: int
    latitude: float
    longitude: float
    price_per_night: Decimal
    photo_url: str
    amenities: list[str]
    city: str
    distance_center: float
    distance_airport: float
    distance_beach: float | None = None
    distance_sightseeing: float | None = None
    id: str | None = None

    def __post_init__(self):
        if not self.id:
            import hashlib
            key = f"{self.type}:{self.city}:{self.name}:{self.latitude}:{self.longitude}".lower()
            self.id = hashlib.md5(key.encode()).hexdigest()

