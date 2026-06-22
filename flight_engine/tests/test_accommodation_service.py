import pytest
from unittest.mock import patch, AsyncMock
from services.accommodation_service import accommodation_service, is_point_in_polygon


def test_is_point_in_polygon():
    # Square polygon
    poly = [[0, 0], [0, 10], [10, 10], [10, 0]]

    # Point inside
    assert is_point_in_polygon(5, 5, poly) is True
    # Point outside
    assert is_point_in_polygon(12, 12, poly) is False


@pytest.mark.asyncio
async def test_get_accommodations_by_city_cache_hit():
    mock_cached = [
        {
            "id": "1",
            "name": "Test Hotel",
            "type": "hotel",
            "rating": 9.0,
            "stars": 5,
            "reviews_count": 100,
            "latitude": 0.0,
            "longitude": 0.0,
            "price_per_night": "200.00",
            "photo_url": "url",
            "amenities": ["Wi-Fi"],
            "city": "SAO",
            "distance_center": 1.0,
            "distance_airport": 5.0,
            "distance_beach": None,
            "distance_sightseeing": None,
        }
    ]
    with patch("services.accommodation_service.cache_service.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_cached
        res = await accommodation_service.get_accommodations_by_city("SAO")
        assert len(res) == 1
        assert res[0]["name"] == "Test Hotel"


@pytest.mark.asyncio
async def test_get_accommodations_by_city_lock_retry():
    mock_cached = [
        {
            "id": "1",
            "name": "Test Hotel",
            "type": "hotel",
            "rating": 9.0,
            "stars": 5,
            "reviews_count": 100,
            "latitude": 0.0,
            "longitude": 0.0,
            "price_per_night": "200.00",
            "photo_url": "url",
            "amenities": ["Wi-Fi"],
            "city": "SAO",
            "distance_center": 1.0,
            "distance_airport": 5.0,
            "distance_beach": None,
            "distance_sightseeing": None,
        }
    ]

    # Simulate first get returns None, second get (inside lock check) returns cached_data
    with (
        patch("services.accommodation_service.cache_service.get", new_callable=AsyncMock) as mock_get,
        patch("services.accommodation_service.cache_service.lock") as mock_lock,
    ):

        # Mocking lock context manager acquiring = False (already locked by another search process)
        lock_mock = AsyncMock()
        lock_mock.__aenter__ = AsyncMock(return_value=False)  # failed to acquire
        lock_mock.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = lock_mock

        # first call returns None, subsequent retries return cached_data
        mock_get.side_effect = [None, mock_cached]

        res = await accommodation_service.get_accommodations_by_city("SAO")
        assert len(res) == 1
        assert res[0]["name"] == "Test Hotel"


@pytest.mark.asyncio
async def test_search_accommodations_filtering():
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
            "amenities": ["Wi-Fi", "Piscina"],
            "city": "FOR",
            "distance_center": 1.0,
            "distance_airport": 5.0,
            "distance_beach": 0.1,
            "distance_sightseeing": None,
        },
        {
            "id": "2",
            "name": "Budget Hostel",
            "type": "hostel",
            "rating": 8.0,
            "stars": 3,
            "reviews_count": 50,
            "latitude": 2.0,
            "longitude": 2.0,
            "price_per_night": "100.00",
            "photo_url": "url",
            "amenities": ["Wi-Fi"],
            "city": "FOR",
            "distance_center": 2.0,
            "distance_airport": 8.0,
            "distance_beach": 1.0,
            "distance_sightseeing": None,
        },
    ]

    with patch(
        "services.accommodation_service.accommodation_service.get_accommodations_by_city", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_hotels

        # Test max price filter
        res = await accommodation_service.search_accommodations(
            city="FOR", checkin_date="2026-06-22", checkout_date="2026-06-24", max_price=200.0
        )
        assert len(res) == 1
        assert res[0]["name"] == "Budget Hostel"
        assert res[0]["nights"] == 2
        assert res[0]["price_total"] == "200.0"

        # Test min price filter
        res = await accommodation_service.search_accommodations(
            city="FOR", checkin_date="2026-06-22", checkout_date="2026-06-24", min_price=400.0
        )
        assert len(res) == 1
        assert res[0]["name"] == "Luxury Hotel"

        # Test star filter
        res = await accommodation_service.search_accommodations(
            city="FOR", checkin_date="2026-06-22", checkout_date="2026-06-24", stars=[5]
        )
        assert len(res) == 1
        assert res[0]["name"] == "Luxury Hotel"

        # Test amenities filter
        res = await accommodation_service.search_accommodations(
            city="FOR", checkin_date="2026-06-22", checkout_date="2026-06-24", amenities=["Piscina"]
        )
        assert len(res) == 1
        assert res[0]["name"] == "Luxury Hotel"

        # Test bounds filter (point 1.0, 1.0 is in bounds north=2.5, south=0.5, east=2.5, west=0.5)
        res = await accommodation_service.search_accommodations(
            city="FOR",
            checkin_date="2026-06-22",
            checkout_date="2026-06-24",
            bounds={"north": 1.5, "south": 0.5, "east": 1.5, "west": 0.5},
        )
        assert len(res) == 1
        assert res[0]["name"] == "Luxury Hotel"

        # Test polygon area filter (within 0,0 to 1.5,1.5)
        res = await accommodation_service.search_accommodations(
            city="FOR",
            checkin_date="2026-06-22",
            checkout_date="2026-06-24",
            polygon=[[0.0, 0.0], [0.0, 1.5], [1.5, 1.5], [1.5, 0.0]],
        )
        assert len(res) == 1
        assert res[0]["name"] == "Luxury Hotel"

        # Test types filter
        res = await accommodation_service.search_accommodations(
            city="FOR", checkin_date="2026-06-22", checkout_date="2026-06-24", types=["hostel"]
        )
        assert len(res) == 1
        assert res[0]["name"] == "Budget Hostel"

        # Test rating filter
        res = await accommodation_service.search_accommodations(
            city="FOR", checkin_date="2026-06-22", checkout_date="2026-06-24", rating=9.0
        )
        assert len(res) == 1
        assert res[0]["name"] == "Luxury Hotel"
