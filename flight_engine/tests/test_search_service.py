import pytest
from unittest.mock import patch, AsyncMock
from decimal import Decimal
from datetime import datetime
from domain.entities import Flight
from application.dto.flight_dto import SearchFlightRequest
from services.search_service import search_service


@pytest.fixture
def sample_flights():
    return [
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
        ),
        Flight(
            id="f2",
            airline="Gol",
            origin="GRU",
            destination="FOR",
            departure_date=datetime(2026, 6, 22, 11, 0),
            arrival_date=datetime(2026, 6, 22, 13, 30),
            price=Decimal("400.00"),
            currency="BRL",
            base_price_brl=Decimal("400.00"),
            duration=150,
            stops=1,
            cabin_class="ECONOMY",
            booking_url="url",
        ),
    ]


def test_strategies_sorting(sample_flights):
    # Cheapest: Gol (400) should be first, then Latam (500)
    sorted_flights = search_service._apply_strategy(sample_flights, "cheapest")
    assert sorted_flights[0].airline == "Gol"

    # Fastest: Gol (150 mins) should be first, then Latam (180 mins)
    sorted_flights = search_service._apply_strategy(sample_flights, "fastest")
    assert sorted_flights[0].airline == "Gol"


@pytest.mark.asyncio
async def test_search_cache_hit(sample_flights):
    req = SearchFlightRequest(
        origin="GRU", destination="FOR", departure_date="2026-06-22", adults=1, strategy="cheapest"
    )
    serialized = search_service._serialize(sample_flights)

    with patch("services.search_service.cache_service.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = serialized
        res = await search_service.search_v2(req)
        assert len(res) == 2
        assert res[0].airline == "Gol"


@pytest.mark.asyncio
async def test_search_cache_miss_lock(sample_flights):
    req = SearchFlightRequest(
        origin="GRU", destination="FOR", departure_date="2026-06-22", adults=1, strategy="cheapest"
    )

    # Mocking cache miss
    with (
        patch("services.search_service.cache_service.get", new_callable=AsyncMock) as mock_get,
        patch("services.search_service.cache_service.set", new_callable=AsyncMock) as mock_set,
        patch("services.search_service.cache_service.lock") as mock_lock,
        patch("services.search_service.SearchService._fetch_from_all_collectors", new_callable=AsyncMock) as mock_fetch,
    ):

        mock_get.return_value = None
        mock_fetch.return_value = sample_flights

        # Setup lock mock
        lock_context = AsyncMock()
        lock_context.__aenter__ = AsyncMock(return_value=True)
        lock_context.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = lock_context

        res = await search_service.search_v2(req)
        assert len(res) == 2
        assert res[0].airline == "Gol"
        mock_set.assert_called_once()
