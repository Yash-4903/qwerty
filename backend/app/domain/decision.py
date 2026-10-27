"""Domain logic for decision support, uncertainty bands, and shortfall buffers.

No I/O or API frameworks.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def compute_uncertainty_band(
    forecast_mw: float | None,
    signed_quantiles: dict[str, float | None],
) -> tuple[float | None, float | None]:
    """Compute empirical prediction bounds for a forecast value: [band_low, band_high].

    Error is defined as (forecast - actual).
    - q90 (90th percentile of signed error) is typically positive: represents over-forecast risk.
      Lower bound = forecast - max(q90, 0)
    - q10 (10th percentile of signed error) is typically negative: represents under-forecast.
      Upper bound = forecast - min(q10, 0)  [subtracting negative value adds to forecast]
    """
    if forecast_mw is None or math.isnan(forecast_mw):
        return None, None

    q90 = (
        signed_quantiles.get("signed_p90")
        if "signed_p90" in signed_quantiles
        else signed_quantiles.get("p90")
    )
    q10 = (
        signed_quantiles.get("signed_p10")
        if "signed_p10" in signed_quantiles
        else signed_quantiles.get("p10")
    )

    q90_val = float(q90) if q90 is not None and not math.isnan(q90) else 0.0
    q10_val = float(q10) if q10 is not None and not math.isnan(q10) else 0.0

    band_low = max(0.0, forecast_mw - max(q90_val, 0.0))
    band_high = max(band_low, forecast_mw - min(q10_val, 0.0))
    return round(band_low, 1), round(band_high, 1)


def compute_decision_output(
    forecast_series: pd.Series,
    signed_quantiles: dict[str, float | None],
    n_history_slots: int,
    band_source: str = "prior_dates",
) -> dict[str, Any]:
    """Synthesise slot-level forecasts and historical error statistics into actionable decision support."""
    valid_fc = forecast_series.dropna()
    if valid_fc.empty:
        return {
            "avg_forecast_mw": None,
            "peak_forecast_mw": None,
            "trough_forecast_mw": None,
            "shortfall_buffer_mw": None,
            "summary": "No forecast data available at this cutoff for the selected delivery day.",
            "n_history_slots": n_history_slots,
            "band_source": band_source,
        }

    avg_fc = float(valid_fc.mean())
    peak_fc = float(valid_fc.max())
    trough_fc = float(valid_fc.min())

    q90 = (
        signed_quantiles.get("signed_p90")
        if "signed_p90" in signed_quantiles
        else signed_quantiles.get("p90")
    )
    buffer_val: float | None = None
    if q90 is not None and not math.isnan(float(q90)):
        # Shortfall buffer must be >= 0 (protection against over-forecast)
        buffer_val = round(max(0.0, float(q90)), 1)

    if buffer_val is not None:
        buf_str = f"~{int(round(buffer_val)):,} MW"
    else:
        buf_str = "insufficient historical data"

    fallback_note = ""
    if band_source == "full_month_fallback":
        fallback_note = " (Note: Fewer than 3 prior days available; fall back to full-month error quantiles used)."

    summary = (
        f"Forecast wind generation averages {int(round(avg_fc)):,} MW across the delivery day "
        f"(peak {int(round(peak_fc)):,} MW, trough {int(round(trough_fc)):,} MW). "
        f"Based on historical forecast errors across {n_history_slots:,} half-hour slots, "
        f"actual generation fell up to {buf_str} below forecast 90% of the time. "
        f"Consider a shortfall buffer of {buf_str} when procuring backup thermal capacity.{fallback_note}"
    )

    return {
        "avg_forecast_mw": round(avg_fc, 1),
        "peak_forecast_mw": round(peak_fc, 1),
        "trough_forecast_mw": round(trough_fc, 1),
        "shortfall_buffer_mw": buffer_val,
        "summary": summary,
        "n_history_slots": n_history_slots,
        "band_source": band_source,
    }
