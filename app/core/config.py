from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ElderCare API"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./eldercare.db"
    secret_key: str = "change-me-to-a-long-random-string"
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"
    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
