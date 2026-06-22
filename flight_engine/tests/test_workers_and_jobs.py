import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from workers.tasks import save_flights_task, scrape_and_cache_flights_task
from events.handlers import (
    handle_flight_search_completed,
    handle_cache_miss,
    handle_cache_hit,
    handle_collector_failed,
    register_handlers,
)
from jobs.scheduler import setup_scheduler


@pytest.mark.asyncio
async def test_save_flights_task():
    flights = [
        {
            "id": "f1",
            "airline": "Latam",
            "origin": "GRU",
            "destination": "FOR",
            "departure_date": "2026-06-22T10:00:00",
            "arrival_date": "2026-06-22T13:00:00",
            "price": "500.00",
            "currency": "BRL",
            "base_price_brl": "500.00",
            "duration": 180,
            "stops": 0,
            "cabin_class": "ECONOMY",
            "booking_url": "url",
            "collected_at": "2026-06-22T08:00:00",
        }
    ]
    with (
        patch("workers.tasks.AsyncSessionLocal", new_callable=MagicMock) as mock_session_cls,
        patch("workers.tasks.asyncio.run") as mock_run,
    ):

        session = AsyncMock()
        mock_session_cls.return_value = session
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)

        # Call task
        save_flights_task(flights)

        # Validate task ran save_flights_async via mock_run
        mock_run.assert_called_once()


def test_scrape_and_cache_flights_task():
    with patch("subprocess.run") as mock_sub:
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_sub.return_value = mock_res

        scrape_and_cache_flights_task("GRU", "FOR", "2026-06-22", "AZUL", "cheapest")
        mock_sub.assert_called_once()


@pytest.mark.asyncio
async def test_event_handlers():
    # Test cache hit
    with patch("events.handlers.logger") as mock_logger:
        await handle_cache_hit({"cache_key": "test_key"})
        mock_logger.info.assert_called_once()

    # Test cache miss
    with patch("events.handlers.logger") as mock_logger:
        await handle_cache_miss({"cache_key": "test_key"})
        mock_logger.info.assert_called_once()

    # Test collector failed
    with patch("events.handlers.logger") as mock_logger:
        await handle_collector_failed({"collector_name": "AZUL", "error": "timeout"})
        mock_logger.error.assert_called_once()

    # Test search completed triggers save task
    with patch("events.handlers.save_flights_task.send") as mock_send:
        await handle_flight_search_completed({"cache_hit": False, "flights": [{"id": "1"}]})
        mock_send.assert_called_once()


def test_register_handlers():
    with patch("events.handlers.event_bus.subscribe") as mock_sub:
        register_handlers()
        assert mock_sub.call_count == 4


def test_setup_scheduler():
    with patch("jobs.scheduler.scheduler") as mock_sched:
        setup_scheduler()
        mock_sched.add_job.assert_called()
        mock_sched.start.assert_called_once()
