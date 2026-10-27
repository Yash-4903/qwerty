"""Hand-built fixtures with deterministic values for unit and integration testing."""

from __future__ import annotations

from datetime import timezone

import pandas as pd

UTC = timezone.utc

# 2026-01-14 is decision day; 2026-01-15 is delivery day
DELIVERY_DAY_STR = "2026-01-15"

SAMPLE_FORECASTS_DATA = [
    # Slot 00:00: Published 07:00 (1000MW), 08:30 (1100MW, latest <= 09:00), 09:30 (1200MW, after 09:00 cutoff)
    {
        "start_time": f"{DELIVERY_DAY_STR}T00:00:00Z",
        "publish_time": "2026-01-14T07:00:00Z",
        "forecast_mw": 1000.0,
    },
    {
        "start_time": f"{DELIVERY_DAY_STR}T00:00:00Z",
        "publish_time": "2026-01-14T08:30:00Z",
        "forecast_mw": 1100.0,
    },
    {
        "start_time": f"{DELIVERY_DAY_STR}T00:00:00Z",
        "publish_time": "2026-01-14T09:30:00Z",
        "forecast_mw": 1200.0,
    },
    # Slot 00:30: Published exactly at cutoff 09:00:00Z (800MW)
    {
        "start_time": f"{DELIVERY_DAY_STR}T00:30:00Z",
        "publish_time": "2026-01-14T09:00:00Z",
        "forecast_mw": 800.0,
    },
    # Slot 01:00: Only published AFTER cutoff (at 10:00:00Z) -> should result in missing forecast
    {
        "start_time": f"{DELIVERY_DAY_STR}T01:00:00Z",
        "publish_time": "2026-01-14T10:00:00Z",
        "forecast_mw": 1500.0,
    },
    # Slot 01:30: Multiple forecasts published at identical time -> deterministic selection
    {
        "start_time": f"{DELIVERY_DAY_STR}T01:30:00Z",
        "publish_time": "2026-01-14T06:00:00Z",
        "forecast_mw": 750.0,
    },
    {
        "start_time": f"{DELIVERY_DAY_STR}T01:30:00Z",
        "publish_time": "2026-01-14T06:00:00Z",
        "forecast_mw": 700.0,
    },
]

SAMPLE_ACTUALS_DATA = [
    # Slot 00:00: actual 950 MW -> error = 1100 - 950 = +150 MW (over-forecast / shortfall)
    {"start_time": f"{DELIVERY_DAY_STR}T00:00:00Z", "generation_mw": 950.0},
    # Slot 00:30: actual 820 MW -> error = 800 - 820 = -20 MW (under-forecast)
    {"start_time": f"{DELIVERY_DAY_STR}T00:30:00Z", "generation_mw": 820.0},
    # Slot 01:00: actual 1400 MW (forecast is missing)
    {"start_time": f"{DELIVERY_DAY_STR}T01:00:00Z", "generation_mw": 1400.0},
    # Slot 01:30: actual 700 MW -> error = 750 - 700 = +50 MW
    {"start_time": f"{DELIVERY_DAY_STR}T01:30:00Z", "generation_mw": 700.0},
]


def get_sample_forecasts_df() -> pd.DataFrame:
    df = pd.DataFrame(SAMPLE_FORECASTS_DATA)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
    df["forecast_mw"] = df["forecast_mw"].astype(float)
    return df


def get_sample_actuals_df() -> pd.DataFrame:
    df = pd.DataFrame(SAMPLE_ACTUALS_DATA)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["generation_mw"] = df["generation_mw"].astype(float)
    return df
