from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class KpiSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mae: float | None = None
    rmse: float | None = None
    bias: float | None = None
    wmape: float | None = None
    n: int
    p50_abs_error: float | None = None
    p90_abs_error: float | None = None
    p95_abs_error: float | None = None
    signed_p5: float | None = None
    signed_p10: float | None = None
    signed_p50: float | None = None
    signed_p90: float | None = None
    signed_p95: float | None = None
    n_missing_forecast: int = 0
    n_missing_actual: int = 0


class HorizonRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bucket: str
    n: int
    mae: float | None = None
    rmse: float | None = None
    bias: float | None = None


class HourRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hour: int
    n: int
    mae: float | None = None
    bias: float | None = None


class DayRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: str
    n: int
    mae: float | None = None
    rmse: float | None = None
    bias: float | None = None


class MetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_date: date
    end_date: date
    cutoff: str
    kpis: KpiSchema
    by_hour: list[HourRow]
    by_horizon: list[HorizonRow]
    by_day: list[DayRow]
