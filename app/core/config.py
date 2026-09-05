from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = "ApplyStack"
    version: str = "0.1.0"
    environment: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://applystack:applystack@localhost:5432/applystack"
    )
    # Log every SQL statement or not. Separate from DEBUG on purpose.
    # Takes the value from the .env file, but defaults to False if not present.
    sql_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
