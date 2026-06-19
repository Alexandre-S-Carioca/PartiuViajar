import httpx
from core.config import settings

class HttpClientFactory:
    _client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            limits = httpx.Limits(
                max_connections=settings.HTTP_MAX_CONNECTIONS,
                max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
            )
            timeout = httpx.Timeout(settings.HTTP_TIMEOUT)
            cls._client = httpx.AsyncClient(limits=limits, timeout=timeout)
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
