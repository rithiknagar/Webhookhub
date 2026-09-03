from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WebhookHub"
    environment: str = "development"
    debug: bool = False

    database_url: str="postgresql+asyncpg://webhookhub:webhookhub@localhost:5432/webhookhub"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()