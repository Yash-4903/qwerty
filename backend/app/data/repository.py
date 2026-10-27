"""In-memory data repository for actuals and forecasts.

Loads parquet files once at startup into memory.
"""

from __future__ import annotations

import logging
import pathlib

import pandas as pd

logger = logging.getLogger(__name__)


class DataRepository:
    def __init__(self) -> None:
        self._actuals: pd.DataFrame | None = None
        self._forecasts: pd.DataFrame | None = None
        self._loaded: bool = False

    def load(self, actuals_path: pathlib.Path, forecasts_path: pathlib.Path) -> None:
        """Load parquet files into memory, validating and standardizing timestamps."""
        logger.info("Loading actuals from %s", actuals_path)
        actuals = pd.read_parquet(actuals_path)
        if "start_time" in actuals.columns and actuals["start_time"].dt.tz is None:
            actuals["start_time"] = actuals["start_time"].dt.tz_localize("UTC")
        self._actuals = actuals.sort_values("start_time").reset_index(drop=True)

        logger.info("Loading forecasts from %s", forecasts_path)
        forecasts = pd.read_parquet(forecasts_path)
        if "start_time" in forecasts.columns and forecasts["start_time"].dt.tz is None:
            forecasts["start_time"] = forecasts["start_time"].dt.tz_localize("UTC")
        if "publish_time" in forecasts.columns and forecasts["publish_time"].dt.tz is None:
            forecasts["publish_time"] = forecasts["publish_time"].dt.tz_localize("UTC")
        self._forecasts = forecasts.sort_values(["start_time", "publish_time"]).reset_index(
            drop=True
        )

        self._loaded = True
        logger.info(
            "Repository ready: %d actuals, %d forecasts loaded into memory.",
            len(self._actuals),
            len(self._forecasts),
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def actuals(self) -> pd.DataFrame:
        if self._actuals is None:
            return pd.DataFrame(columns=["start_time", "generation_mw"])
        return self._actuals

    @property
    def forecasts(self) -> pd.DataFrame:
        if self._forecasts is None:
            return pd.DataFrame(columns=["start_time", "publish_time", "forecast_mw"])
        return self._forecasts

    def actuals_for_range(self, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> pd.DataFrame:
        if self._actuals is None or self._actuals.empty:
            return pd.DataFrame(columns=["start_time", "generation_mw"])
        mask = (self._actuals["start_time"] >= start_ts) & (self._actuals["start_time"] < end_ts)
        return self._actuals[mask].copy()

    def forecasts_for_delivery_day(self, delivery_day_ts: pd.Timestamp) -> pd.DataFrame:
        if self._forecasts is None or self._forecasts.empty:
            return pd.DataFrame(columns=["start_time", "publish_time", "forecast_mw"])
        start = delivery_day_ts.floor("D")
        end = start + pd.Timedelta(days=1)
        mask = (self._forecasts["start_time"] >= start) & (self._forecasts["start_time"] < end)
        return self._forecasts[mask].copy()

    def forecasts_for_range(self, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> pd.DataFrame:
        if self._forecasts is None or self._forecasts.empty:
            return pd.DataFrame(columns=["start_time", "publish_time", "forecast_mw"])
        mask = (self._forecasts["start_time"] >= start_ts) & (
            self._forecasts["start_time"] < end_ts
        )
        return self._forecasts[mask].copy()


_repo_instance = DataRepository()


def get_repository() -> DataRepository:
    return _repo_instance
