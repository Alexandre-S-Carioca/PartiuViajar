import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from api.main import app
from datetime import datetime
from decimal import Decimal
from domain.entities import Flight

client = TestClient(app)


def test_health_endpoint():
    # Mocking both Redis and DB success
    with (
        patch("api.routes.health.cache_service.redis.ping", new_callable=AsyncMock) as mock_ping,
        patch("api.routes.health.AsyncSessionLocal", new_callable=MagicMock) as mock_session_cls,
    ):

        mock_ping.return_value = True

        # Mock session execute
        mock_session = AsyncMock()
        mock_session_cls.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["redis"] == "connected"
        assert data["database"] == "connected"


def test_metrics_endpoint():
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "requests_total" in res.text


@pytest.mark.asyncio
async def test_hotels_endpoint():
    mock_hotels = [
        {
            "id": "1",
            "name": "Luxury Hotel",
            "type": "hotel",
            "rating": 9.5,
            "stars": 5,
            "reviews_count": 100,
            "latitude": 1.0,
            "longitude": 1.0,
            "price_per_night": "500.00",
            "photo_url": "url",
            "amenities": ["Wi-Fi"],
            "city": "FOR",
            "distance_center": 1.0,
            "distance_airport": 5.0,
            "distance_beach": 0.1,
            "distance_sightseeing": None,
            "nights": 2,
            "price_total": "1000.00",
        }
    ]
    with patch("api.routes.hotels.accommodation_service.search_accommodations", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_hotels
        res = client.get("/api/hotels?destination=FOR&checkin=2026-06-22&checkout=2026-06-24")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["name"] == "Luxury Hotel"


@pytest.mark.asyncio
async def test_flights_endpoint():
    mock_flights = [
        Flight(
            id="f1",
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
            collected_at=datetime.utcnow(),
        )
    ]
    with patch("api.routes.flights_api.search_flights_query_handler.handle", new_callable=AsyncMock) as mock_handle:
        # Pydantic validation handles dict models
        mock_handle.return_value = [
            {
                "id": f.id,
                "airline": f.airline,
                "origin": f.origin,
                "destination": f.destination,
                "departure_date": f.departure_date.isoformat(),
                "arrival_date": f.arrival_date.isoformat(),
                "price": float(f.price),
                "currency": f.currency,
                "base_price_brl": float(f.base_price_brl),
                "duration": f.duration,
                "stops": f.stops,
                "cabin_class": f.cabin_class,
                "booking_url": f.booking_url,
                "collected_at": f.collected_at.isoformat(),
            }
            for f in mock_flights
        ]

        res = client.get("/api/flights?origin=GRU&destination=FOR&departure_date=2026-06-22")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["airline"] == "Latam"


@pytest.mark.asyncio
async def test_travel_endpoint():
    mock_flights = [
        Flight(
            id="f1",
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
            collected_at=datetime.utcnow(),
        )
    ]
    mock_hotels = [
        {
            "id": "1",
            "name": "Luxury Hotel",
            "type": "hotel",
            "rating": 9.5,
            "stars": 5,
            "reviews_count": 100,
            "latitude": 1.0,
            "longitude": 1.0,
            "price_per_night": "500.00",
            "photo_url": "url",
            "amenities": ["Wi-Fi"],
            "city": "FOR",
            "distance_center": 1.0,
            "distance_airport": 5.0,
            "distance_beach": 0.1,
            "distance_sightseeing": None,
            "nights": 2,
            "price_total": "1000.00",
        }
    ]
    with (
        patch("api.routes.travel.search_service.search_v2", new_callable=AsyncMock) as mock_flights_search,
        patch(
            "api.routes.travel.accommodation_service.search_accommodations", new_callable=AsyncMock
        ) as mock_hotels_search,
        patch("api.routes.travel.save_search_history", new_callable=AsyncMock),
    ):

        mock_flights_search.return_value = mock_flights
        mock_hotels_search.return_value = mock_hotels

        res = client.get("/api/travel?origin=GRU&destination=FOR&departure_date=2026-06-22&return_date=2026-06-24")
        assert res.status_code == 200
        data = res.json()
        assert "flights" in data
        assert "accommodations" in data
        assert len(data["flights"]["outbound"]) == 1
        assert len(data["accommodations"]) == 1


@pytest.mark.asyncio
async def test_map_endpoint():
    mock_hotels = [
        {
            "id": "1",
            "name": "Luxury Hotel",
            "type": "hotel",
            "rating": 9.5,
            "stars": 5,
            "reviews_count": 100,
            "latitude": 1.0,
            "longitude": 1.0,
            "price_per_night": "500.00",
            "photo_url": "url",
            "amenities": ["Wi-Fi"],
            "city": "FOR",
            "distance_center": 1.0,
            "distance_airport": 5.0,
            "distance_beach": 0.1,
            "distance_sightseeing": None,
            "nights": 2,
            "price_total": "1000.00",
        }
    ]
    with patch("api.routes.map.accommodation_service.search_accommodations", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_hotels
        res = client.get("/api/map?destination=FOR&checkin=2026-06-22&checkout=2026-06-24")
        assert res.status_code == 200
        data = res.json()
        assert "markers" in data
        assert "heatmap" in data
        assert len(data["markers"]) == 1
        assert data["markers"][0]["marker_color"] == "red"  # > 400 is red


@pytest.mark.asyncio
async def test_favorites_endpoint():
    # Test POST add
    with patch("api.routes.favorites.AsyncSessionLocal", new_callable=MagicMock) as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value = mock_session
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # First execute returns None (doesn't exist)
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_res

        payload = {"item_type": "accommodation", "item_id": "h1", "details": {"name": "Test Hotel"}}
        res = client.post("/api/favorites", json=payload)
        assert res.status_code == 200
        assert res.json()["status"] == "added"

        # Test GET
        mock_fav = MagicMock()
        mock_fav.id = 1
        mock_fav.item_type = "accommodation"
        mock_fav.item_id = "h1"
        mock_fav.details = {"name": "Test Hotel"}
        mock_fav.created_at = datetime.utcnow()

        mock_res_get = MagicMock()
        mock_res_get.scalars.return_value.all.return_value = [mock_fav]
        mock_session.execute.return_value = mock_res_get

        res = client.get("/api/favorites")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["item_id"] == "h1"
