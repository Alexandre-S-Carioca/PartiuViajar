from decimal import Decimal
from infrastructure.acl.azul_adapter import AzulAdapter
from infrastructure.acl.latam_adapter import LatamAdapter
from infrastructure.acl.gol_adapter import GolAdapter
from infrastructure.acl.copa_adapter import CopaAdapter
from infrastructure.acl.avianca_adapter import AviancaAdapter
from infrastructure.acl.tap_adapter import TapAdapter


def test_azul_adapter():
    data = {
        "from": "GRU",
        "to": "FOR",
        "dep": "2026-06-22T10:00:00",
        "arr": "2026-06-22T13:00:00",
        "total_amount": "550.00",
        "curr": "BRL",
        "time_mins": 130,
        "connections": 0,
        "class_type": "ECONOMY",
        "flightId": "AZ789",
    }
    flight = AzulAdapter.normalize(data)
    assert flight.airline == "AZUL"
    assert flight.origin == "GRU"
    assert flight.price == Decimal("550.00")
    assert flight.stops == 0


def test_latam_adapter():
    data = {
        "origin": "GRU",
        "destination": "FOR",
        "departure_time": "2026-06-22T10:00:00",
        "arrival_time": "2026-06-22T13:00:00",
        "fare": "480.00",
        "currency": "BRL",
        "duration_minutes": 180,
        "stops": 0,
        "class": "ECONOMY",
        "flight_id": "LA123",
    }
    flight = LatamAdapter.normalize(data)
    assert flight.airline == "LATAM"
    assert flight.price == Decimal("480.00")


def test_gol_adapter():
    data = {
        "origin_airport": "GRU",
        "destination_airport": "FOR",
        "departure": "2026-06-22T10:00:00",
        "arrival": "2026-06-22T13:00:00",
        "price": "510.00",
        "currency_code": "BRL",
        "duration": 180,
        "stops": 0,
        "cabin": "ECONOMY",
        "id": "G3456",
    }
    flight = GolAdapter.normalize(data)
    assert flight.airline == "GOL"
    assert flight.price == Decimal("510.00")


def test_copa_adapter():
    data = {
        "origin": "GRU",
        "destination": "FOR",
        "departure_datetime": "2026-06-22T10:00:00",
        "arrival_datetime": "2026-06-22T13:00:00",
        "price": "600.00",
        "currency": "BRL",
        "duration": 180,
        "stops": 1,
        "cabin": "ECONOMY",
        "flight_id": "CM789",
    }
    flight = CopaAdapter.normalize(data)
    assert flight.airline == "COPA"
    assert flight.price == Decimal("600.00")


def test_avianca_adapter():
    data = {
        "origin": "GRU",
        "destination": "FOR",
        "dep": "2026-06-22T10:00:00",
        "arr": "2026-06-22T13:00:00",
        "cost": "100.00",
        "currency": "USD",
        "duration_mins": 180,
        "connections": 1,
        "class": "ECONOMY",
        "id": "AV123",
    }
    flight = AviancaAdapter.normalize(data)
    assert flight.airline == "AVIANCA"
    # Will be converted to BRL, assuming 1 USD = 5.0 BRL (mock value)
    assert flight.base_price_brl > 0


def test_tap_adapter():
    data = {
        "from": "GRU",
        "to": "FOR",
        "departure": "2026-06-22T10:00:00",
        "arrival": "2026-06-22T13:00:00",
        "price_eur": "90.00",
        "time": 180,
        "stops": 1,
        "cabin": "ECONOMY",
        "id": "TP123",
    }
    flight = TapAdapter.normalize(data)
    assert flight.airline == "TAP"
    assert flight.base_price_brl > 0
