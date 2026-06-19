import abc
import asyncio
from typing import List
from datetime import datetime
import pybreaker
from tenacity import retry, stop_after_attempt, wait_exponential
from aiolimiter import AsyncLimiter
from factories.http_client_factory import HttpClientFactory
from domain.entities import Flight
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class BaseCollector(abc.ABC):
    def __init__(self, name: str):
        self.name = name
        self.limiter = AsyncLimiter(settings.RATE_LIMIT_RPS, 1)
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=settings.CB_FAIL_MAX,
            reset_timeout=settings.CB_RESET_TIMEOUT
        )

    @abc.abstractmethod
    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int
    ) -> List[Flight]:
        pass

    async def _safe_get(self, url: str, params: dict = None) -> dict:
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            reraise=True
        )
        async def _do_get():
            async with self.limiter:
                client = HttpClientFactory.get_client()
                logger.debug(f"[{self.name}] Fetching {url}")
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        
        return await self.breaker.call_async(_do_get)
