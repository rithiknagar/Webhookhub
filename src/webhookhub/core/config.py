from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "WebhookHub"

    environment: str = "development"

    debug: bool = False

    database_url: str

    redis_url: str

    secret_key: str = Field(min_length=32)

    algorithm: str = "HS256"

    exp_time: int = Field(
        default=120,
        gt=0,
    )
    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()