"""Core domain logic for cutoff selection.

No I/O, no HTTP, no FastAPI imports — pure functions only.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

LONDON_TZ = ZoneInfo("Europe/London")
UTC = timezone.utc


def parse_cutoff_time(cutoff_str: str) -> tuple[int, int]:
    """Parse 'HH:MM' -> (hour, minute). Raises ValueError on invalid format or values."""
    if not isinstance(cutoff_str, str) or not re.match(r"^\d{2}:\d{2}$", cutoff_str):
        raise ValueError(f"Cutoff must be in format HH:MM, got: {cutoff_str!r}")
    hour_str, min_str = cutoff_str.split(":")
    hour = int(hour_str)
    minute = int(min_str)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Cutoff time out of range 00:00-23:59, got: {cutoff_str!r}")
    return hour, minute


def decision_date_to_cutoff_utc(decision_date: date, cutoff_hhmm: str) -> datetime:
    """Convert decision date (D-1) and London cutoff time (HH:MM) to a timezone-aware UTC datetime.

    Uses ZoneInfo("Europe/London") to properly account for daylight saving time (e.g. GMT vs BST).
    """
    hour, minute = parse_cutoff_time(cutoff_hhmm)
    local_dt = datetime(
        decision_date.year,
        decision_date.month,
        decision_date.day,
        hour,
        minute,
        0,
        tzinfo=LONDON_TZ,
    )
    return local_dt.astimezone(timezone.utc)


def delivery_date_from_decision(decision_date: date) -> date:
    """Return delivery day D = decision_date + 1 day."""
    return decision_date + timedelta(days=1)


def generate_expected_half_hours(delivery_day: date) -> list[datetime]:
    """Generate the 48 half-hourly start times for a target delivery day in UTC."""
    start_dt = datetime(
        delivery_day.year, delivery_day.month, delivery_day.day, 0, 0, 0, tzinfo=timezone.utc
    )
    return [start_dt + timedelta(minutes=30 * i) for i in range(48)]


def select_latest_forecast_at_cutoff(
    forecast_df: pd.DataFrame,
    cutoff_utc: datetime,
    expected_start_times: list[datetime] | None = None,
) -> pd.DataFrame:
    """For each half-hourly slot on delivery day, selects the forecast published latest on or before cutoff_utc.

    Returns DataFrame with columns:
        - start_time (datetime, UTC)
        - forecast_mw (float or NaN)
        - publish_time (datetime, UTC or NaT)
        - horizon_h (float or NaN)
        - has_forecast (bool)
    """
    cols = ["start_time", "forecast_mw", "publish_time", "horizon_h", "has_forecast"]

    if expected_start_times:
        base_df = pd.DataFrame({"start_time": pd.to_datetime(expected_start_times, utc=True)})
    elif not forecast_df.empty and "start_time" in forecast_df.columns:
        base_df = pd.DataFrame(
            {
                "start_time": forecast_df["start_time"]
                .drop_duplicates()
                .sort_values()
                .reset_index(drop=True)
            }
        )
    else:
        return pd.DataFrame(columns=cols)

    if forecast_df.empty:
        base_df["forecast_mw"] = float("nan")
        base_df["publish_time"] = pd.NaT
        base_df["horizon_h"] = float("nan")
        base_df["has_forecast"] = False
        return base_df[cols]

    # Ensure tz-aware
    df = forecast_df.copy()
    if df["publish_time"].dt.tz is None:
        df["publish_time"] = df["publish_time"].dt.tz_localize("UTC")
    if df["start_time"].dt.tz is None:
        df["start_time"] = df["start_time"].dt.tz_localize("UTC")

    cutoff_ts = pd.Timestamp(cutoff_utc)
    if cutoff_ts.tz is None:
        cutoff_ts = cutoff_ts.tz_localize("UTC")

    # Candidates: publish_time <= cutoff_utc
    candidates = df[df["publish_time"] <= cutoff_ts].copy()

    if candidates.empty:
        base_df["forecast_mw"] = float("nan")
        base_df["publish_time"] = pd.NaT
        base_df["horizon_h"] = float("nan")
        base_df["has_forecast"] = False
        return base_df[cols]

    # Deterministic sorting: by start_time, then publish_time desc, then forecast_mw desc
    candidates = candidates.sort_values(
        by=["start_time", "publish_time", "forecast_mw"],
        ascending=[True, False, False],
    )
    # Deduplicate by start_time keeping the first (latest publish_time)
    selected = candidates.drop_duplicates(subset=["start_time"], keep="first").copy()

    # Calculate horizon in hours: (start_time - publish_time)
    selected["horizon_h"] = (
        selected["start_time"] - selected["publish_time"]
    ).dt.total_seconds() / 3600.0
    selected["has_forecast"] = True

    merged = base_df.merge(
        selected[["start_time", "forecast_mw", "publish_time", "horizon_h", "has_forecast"]],
        on="start_time",
        how="left",
    )
    merged["has_forecast"] = merged["has_forecast"].fillna(False).astype(bool)
    return merged[cols].sort_values("start_time").reset_index(drop=True)
