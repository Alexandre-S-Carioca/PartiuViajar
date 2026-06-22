import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    return session


@pytest.fixture
def mock_cache_service():
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()

    # Mocking lock context manager
    lock_mock = AsyncMock()
    lock_mock.__aenter__ = AsyncMock(return_value=True)
    lock_mock.__aexit__ = AsyncMock(return_value=None)
    cache.lock = MagicMock(return_value=lock_mock)

    return cache
