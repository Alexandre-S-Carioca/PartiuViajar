from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureFlags(BaseSettings):
    ENABLE_LATAM: bool = True
    ENABLE_GOL: bool = True
    ENABLE_AZUL: bool = True
    ENABLE_COPA: bool = True
    ENABLE_AVIANCA: bool = True
    ENABLE_TAP: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


feature_flags = FeatureFlags()
