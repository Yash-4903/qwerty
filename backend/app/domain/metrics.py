"""Pure domain functions for forecast evaluation metrics.

No I/O or API frameworks.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def mae(errors: pd.Series) -> float | None:
    """Mean Absolute Error (MW)."""
    valid = errors.dropna()
    if valid.empty:
        return None
    val = float(valid.abs().mean())
    return None if math.isnan(val) else val


def rmse(errors: pd.Series) -> float | None:
    """Root Mean Squared Error (MW)."""
    valid = errors.dropna()
    if valid.empty:
        return None
    val = float(math.sqrt((valid**2).mean()))
    return None if math.isnan(val) else val


def bias(errors: pd.Series) -> float | None:
    """Mean signed error (forecast - actual) in MW.

    Positive = over-forecast (shortfall risk for buyer).
    Negative = under-forecast.
    """
    valid = errors.dropna()
    if valid.empty:
        return None
    val = float(valid.mean())
    return None if math.isnan(val) else val


def wmape(errors: pd.Series, actuals: pd.Series) -> float | None:
    """Weighted MAPE = sum(|error|) / sum(actual).

    Avoids division-by-zero or explosion when actual wind is near zero.
    """
    mask = errors.notna() & actuals.notna()
    if not mask.any():
        return None
    valid_err = errors[mask].abs()
    valid_act = actuals[mask]
    total_act = float(valid_act.sum())
    if total_act <= 0.0:
        return None
    val = float(valid_err.sum() / total_act)
    return None if math.isnan(val) else val


def abs_error_quantiles(
    errors: pd.Series, qs: list[float] | None = None
) -> dict[str, float | None]:
    """Empirical quantiles of absolute errors |forecast - actual|."""
    if qs is None:
        qs = [0.50, 0.90, 0.95]
    valid = errors.dropna().abs()
    if valid.empty:
        return {f"p{int(q * 100)}": None for q in qs}
    result: dict[str, float | None] = {}
    for q in qs:
        val = float(valid.quantile(q))
        result[f"p{int(q * 100)}"] = None if math.isnan(val) else val
    return result


def signed_error_quantiles(
    errors: pd.Series, qs: list[float] | None = None
) -> dict[str, float | None]:
    """Empirical quantiles of signed error (forecast - actual).

    Used for buffer sizing and empirical prediction intervals.
    """
    if qs is None:
        qs = [0.05, 0.10, 0.50, 0.90, 0.95]
    valid = errors.dropna()
    if valid.empty:
        return {f"p{int(q * 100)}": None for q in qs}
    result: dict[str, float | None] = {}
    for q in qs:
        val = float(valid.quantile(q))
        result[f"p{int(q * 100)}"] = None if math.isnan(val) else val
    return result


def compute_all_kpis(errors: pd.Series, actuals: pd.Series) -> dict[str, Any]:
    """Calculate all high-level KPIs for a set of paired forecasts and actuals."""
    mask = errors.notna() & actuals.notna()
    valid_err = errors[mask]
    valid_act = actuals[mask]

    abs_q = abs_error_quantiles(valid_err, [0.50, 0.90, 0.95])
    signed_q = signed_error_quantiles(valid_err, [0.05, 0.10, 0.50, 0.90, 0.95])

    return {
        "mae": mae(valid_err),
        "rmse": rmse(valid_err),
        "bias": bias(valid_err),
        "wmape": wmape(valid_err, valid_act),
        "n": int(mask.sum()),
        "p50_abs_error": abs_q.get("p50"),
        "p90_abs_error": abs_q.get("p90"),
        "p95_abs_error": abs_q.get("p95"),
        "signed_p5": signed_q.get("p5"),
        "signed_p10": signed_q.get("p10"),
        "signed_p50": signed_q.get("p50"),
        "signed_p90": signed_q.get("p90"),
        "signed_p95": signed_q.get("p95"),
    }


HORIZON_BUCKETS = [
    (0.0, 6.0, "0-6h"),
    (6.0, 12.0, "6-12h"),
    (12.0, 24.0, "12-24h"),
    (24.0, 36.0, "24-36h"),
    (36.0, 48.0, "36-48h"),
    (48.0, 72.0, "48-72h"),
    (72.0, float("inf"), "72h+"),
]


def _horizon_bucket_label(horizon_h: float) -> str:
    for low, high, label in HORIZON_BUCKETS:
        if low <= horizon_h < high:
            return label
    return "72h+"


def metrics_by_horizon(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Compute error statistics per forecast horizon bucket.

    Expects columns: 'horizon_h', 'error_mw'.
    """
    if df.empty or "horizon_h" not in df.columns or "error_mw" not in df.columns:
        return []

    valid = df.dropna(subset=["horizon_h", "error_mw"]).copy()
    if valid.empty:
        return []

    valid["bucket"] = valid["horizon_h"].apply(_horizon_bucket_label)

    results: list[dict[str, Any]] = []
    for _, _, label in HORIZON_BUCKETS:
        subset = valid[valid["bucket"] == label]
        if subset.empty:
            continue
        errs = subset["error_mw"]
        results.append(
            {
                "bucket": label,
                "n": int(len(errs)),
                "mae": mae(errs),
                "rmse": rmse(errs),
                "bias": bias(errs),
            }
        )
    return results


def metrics_by_hour(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Compute error statistics per hour of day (0..23).

    Expects columns: 'start_time', 'error_mw'.
    """
    if df.empty or "start_time" not in df.columns or "error_mw" not in df.columns:
        return []

    valid = df.dropna(subset=["start_time", "error_mw"]).copy()
    if valid.empty:
        return []

    valid["hour"] = valid["start_time"].dt.hour

    results: list[dict[str, Any]] = []
    for h in range(24):
        subset = valid[valid["hour"] == h]
        if subset.empty:
            continue
        errs = subset["error_mw"]
        results.append(
            {
                "hour": h,
                "n": int(len(errs)),
                "mae": mae(errs),
                "bias": bias(errs),
            }
        )
    return results


def metrics_by_day(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Compute error statistics by date (daily MAE, RMSE, bias).

    Expects columns: 'start_time', 'error_mw'.
    """
    if df.empty or "start_time" not in df.columns or "error_mw" not in df.columns:
        return []

    valid = df.dropna(subset=["start_time", "error_mw"]).copy()
    if valid.empty:
        return []

    valid["date_str"] = valid["start_time"].dt.strftime("%Y-%m-%d")

    results: list[dict[str, Any]] = []
    for date_str, group in valid.groupby("date_str"):
        errs = group["error_mw"]
        results.append(
            {
                "date": str(date_str),
                "n": int(len(errs)),
                "mae": mae(errs),
                "rmse": rmse(errs),
                "bias": bias(errs),
            }
        )
    return sorted(results, key=lambda x: str(x["date"]))
