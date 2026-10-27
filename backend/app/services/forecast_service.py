"""Service orchestrating cutoff selection and decision support for a single decision date."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from app.data.repository import DataRepository
from app.domain.cutoff import (
    decision_date_to_cutoff_utc,
    delivery_date_from_decision,
    generate_expected_half_hours,
    select_latest_forecast_at_cutoff,
)
from app.domain.decision import compute_decision_output, compute_uncertainty_band
from app.domain.metrics import signed_error_quantiles
from app.schemas.forecast import DecisionSchema, ForecastResponse, SlotSchema

logger = logging.getLogger(__name__)
LONDON_TZ = ZoneInfo("Europe/London")


def get_forecast_for_decision_date(
    repo: DataRepository,
    decision_date: date,
    cutoff_hhmm: str,
) -> ForecastResponse:
    delivery_date = delivery_date_from_decision(decision_date)
    cutoff_utc = decision_date_to_cutoff_utc(decision_date, cutoff_hhmm)
    cutoff_london = cutoff_utc.astimezone(LONDON_TZ).strftime("%H:%M %Z")

    expected_slots = generate_expected_half_hours(delivery_date)
    delivery_ts = pd.Timestamp(delivery_date, tz="UTC")

    forecasts_df = repo.forecasts_for_delivery_day(delivery_ts)
    selected_fc = select_latest_forecast_at_cutoff(forecasts_df, cutoff_utc, expected_slots)

    actuals_df = repo.actuals_for_range(delivery_ts, delivery_ts + pd.Timedelta(days=1))
    actuals_map: dict[pd.Timestamp, float] = {}
    if not actuals_df.empty:
        actuals_map = actuals_df.set_index("start_time")["generation_mw"].to_dict()

    # Calculate historical signed-error quantiles (no look-ahead)
    signed_q, n_hist, band_source = _calculate_historical_error_quantiles(
        repo, decision_date, cutoff_hhmm
    )

    slots: list[SlotSchema] = []
    n_missing_fc = 0
    n_missing_act = 0

    for _, row in selected_fc.iterrows():
        st_ts = pd.Timestamp(row["start_time"])
        fc_val = (
            float(row["forecast_mw"])
            if row["has_forecast"] and pd.notna(row["forecast_mw"])
            else None
        )
        act_val = actuals_map.get(st_ts)
        if act_val is not None:
            act_val = float(act_val)

        err_val = (fc_val - act_val) if (fc_val is not None and act_val is not None) else None

        band_low, band_high = compute_uncertainty_band(fc_val, signed_q)

        if not row["has_forecast"] or fc_val is None:
            n_missing_fc += 1
        if act_val is None:
            n_missing_act += 1

        pub_time = row["publish_time"]
        pub_dt = (
            pub_time.to_pydatetime()
            if pd.notna(pub_time) and hasattr(pub_time, "to_pydatetime")
            else None
        )
        horizon_h = float(row["horizon_h"]) if pd.notna(row.get("horizon_h")) else None

        slots.append(
            SlotSchema(
                start_time=st_ts.to_pydatetime(),
                forecast_mw=round(fc_val, 1) if fc_val is not None else None,
                actual_mw=round(act_val, 1) if act_val is not None else None,
                error_mw=round(err_val, 1) if err_val is not None else None,
                publish_time=pub_dt,
                horizon_h=round(horizon_h, 1) if horizon_h is not None else None,
                band_low=band_low,
                band_high=band_high,
                has_forecast=bool(row["has_forecast"] and fc_val is not None),
            )
        )

    fc_series = pd.Series([s.forecast_mw for s in slots], dtype=float)
    decision_dict = compute_decision_output(fc_series, signed_q, n_hist, band_source)

    return ForecastResponse(
        decision_date=decision_date,
        delivery_date=delivery_date,
        cutoff_utc=cutoff_utc,
        cutoff_london=cutoff_london,
        slots=slots,
        n_missing_forecast=n_missing_fc,
        n_missing_actual=n_missing_act,
        total_slots=len(slots),
        decision=DecisionSchema(**decision_dict),
    )


def _calculate_historical_error_quantiles(
    repo: DataRepository,
    current_decision_date: date,
    cutoff_hhmm: str,
) -> tuple[dict[str, float | None], int, str]:
    """Compute signed error quantiles strictly prior to current_decision_date.

    If fewer than 3 prior days are available, falls back to full-month historical data.
    """
    prior_dates: list[date] = []
    d = date(2026, 1, 1)
    while d < current_decision_date:
        prior_dates.append(d)
        d += timedelta(days=1)

    band_source = "prior_dates"
    if len(prior_dates) < 3:
        # Fallback to all available January dates
        prior_dates = [date(2026, 1, day) for day in range(1, 32)]
        band_source = "full_month_fallback"

    collected_errors: list[float] = []

    for d_date in prior_dates:
        del_date = delivery_date_from_decision(d_date)
        cut_utc = decision_date_to_cutoff_utc(d_date, cutoff_hhmm)
        del_ts = pd.Timestamp(del_date, tz="UTC")

        fc_df = repo.forecasts_for_delivery_day(del_ts)
        if fc_df.empty:
            continue
        exp_slots = generate_expected_half_hours(del_date)
        selected = select_latest_forecast_at_cutoff(fc_df, cut_utc, exp_slots)

        act_df = repo.actuals_for_range(del_ts, del_ts + pd.Timedelta(days=1))
        if act_df.empty:
            continue
        act_map = act_df.set_index("start_time")["generation_mw"].to_dict()

        for _, row in selected.iterrows():
            if not row["has_forecast"] or pd.isna(row["forecast_mw"]):
                continue
            act_mw = act_map.get(pd.Timestamp(row["start_time"]))
            if act_mw is not None:
                err = float(row["forecast_mw"]) - float(act_mw)
                collected_errors.append(err)

    if not collected_errors:
        return {}, 0, band_source

    err_series = pd.Series(collected_errors, dtype=float)
    quantiles = signed_error_quantiles(err_series, [0.05, 0.10, 0.50, 0.90, 0.95])
    return quantiles, len(collected_errors), band_source
