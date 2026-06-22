from datetime import datetime
from decimal import Decimal
from domain.entities import Flight, Accommodation


def test_flight_entity_id_generation():
    f = Flight(
        airline="Latam",
        origin="GRU",
        destination="FOR",
        departure_date=datetime(2026, 6, 22, 10, 0),
        arrival_date=datetime(2026, 6, 22, 13, 0),
        price=Decimal("500.00"),
        currency="BRL",
        base_price_brl=Decimal("500.00"),
        duration=180,
        stops=0,
        cabin_class="ECONOMY",
        booking_url="url",
    )
    assert f.id is not None
    assert len(f.id) == 32  # MD5 length


def test_accommodation_entity_id_generation():
    a = Accommodation(
        name="Hotel Pullman",
        type="hotel",
        rating=9.0,
        stars=5,
        reviews_count=200,
        latitude=-23.5855,
        longitude=-46.6522,
        price_per_night=Decimal("380.00"),
        photo_url="url",
        amenities=["Wi-Fi"],
        city="SAO",
        distance_center=5.2,
        distance_airport=6.8,
    )
    assert a.id is not None
    assert len(a.id) == 32
