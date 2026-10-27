from __future__ import annotations

import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = pathlib.Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Data
    actuals_path: pathlib.Path = ROOT_DIR / "data" / "processed" / "actuals.parquet"
    forecasts_path: pathlib.Path = ROOT_DIR / "data" / "processed" / "forecasts.parquet"

    # API
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:8000", "*"])
    api_prefix: str = "/api/v1"

    # Domain
    default_cutoff_time: str = "09:00"  # HH:MM London time
    timezone: str = "Europe/London"

    # Decision window
    min_decision_date: str = "2026-01-01"  # D-1 dates in January 2026
    max_decision_date: str = "2026-01-31"

    # Server
    port: int = Field(default=8000, alias="PORT")
    log_level: str = "INFO"
    environment: str = "development"

    # Elexon (for ingestion only)
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    elexon_api_key: str = Field(default="", alias="ELEXON_API_KEY")


settings = Settings()
