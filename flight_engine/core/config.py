from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Flight Search Engine"
    DEBUG: bool = False

    # HTTP Client
    HTTP_MAX_CONNECTIONS: int = 100
    HTTP_MAX_KEEPALIVE_CONNECTIONS: int = 20
    HTTP_TIMEOUT: int = 5

    # Database
    DB_USER: str = "alexandre"
    DB_PASSWORD: str = "123456"
    DB_HOST: str = "192.168.0.150"
    DB_PORT: str = "5432"
    DB_NAME: str = "partiu_viajar"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis
    REDIS_URL: str = "redis://192.168.0.150:6379/0"

    # Rate Limiting & Circuit Breaker
    RATE_LIMIT_RPS: int = 5
    CB_FAIL_MAX: int = 5
    CB_RESET_TIMEOUT: int = 60

    # Cache
    CACHE_TTL_MINUTES: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
