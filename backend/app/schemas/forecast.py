from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SlotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_time: datetime
    forecast_mw: float | None = None
    actual_mw: float | None = None
    error_mw: float | None = None
    publish_time: datetime | None = None
    horizon_h: float | None = None
    band_low: float | None = None
    band_high: float | None = None
    has_forecast: bool = True


class DecisionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    avg_forecast_mw: float | None = None
    peak_forecast_mw: float | None = None
    trough_forecast_mw: float | None = None
    shortfall_buffer_mw: float | None = None
    summary: str
    n_history_slots: int
    band_source: str


class ForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_date: date
    delivery_date: date
    cutoff_utc: datetime
    cutoff_london: str
    slots: list[SlotSchema]
    n_missing_forecast: int
    n_missing_actual: int
    total_slots: int
    decision: DecisionSchema
