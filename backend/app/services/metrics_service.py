"""Service orchestrating aggregated metrics, breakdowns, and CSV export."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import pandas as pd

from app.data.repository import DataRepository
from app.domain.cutoff import (
    decision_date_to_cutoff_utc,
    delivery_date_from_decision,
    generate_expected_half_hours,
    select_latest_forecast_at_cutoff,
)
from app.domain.metrics import (
    compute_all_kpis,
    metrics_by_day,
    metrics_by_horizon,
    metrics_by_hour,
)
from app.schemas.metrics import (
    DayRow,
    HorizonRow,
    HourRow,
    KpiSchema,
    MetricsResponse,
)

logger = logging.getLogger(__name__)


def get_metrics_for_range(
    repo: DataRepository,
    start_decision: date,
    end_decision: date,
    cutoff_hhmm: str,
) -> MetricsResponse:
    cutoff_slots: list[dict[str, Any]] = []
    n_missing_fc = 0
    n_missing_act = 0

    curr = start_decision
    while curr <= end_decision:
        delivery_date = delivery_date_from_decision(curr)
        cutoff_utc = decision_date_to_cutoff_utc(curr, cutoff_hhmm)
        del_ts = pd.Timestamp(delivery_date, tz="UTC")

        fc_df = repo.forecasts_for_delivery_day(del_ts)
        exp_slots = generate_expected_half_hours(delivery_date)
        selected = select_latest_forecast_at_cutoff(fc_df, cutoff_utc, exp_slots)

        act_df = repo.actuals_for_range(del_ts, del_ts + pd.Timedelta(days=1))
        act_map: dict[pd.Timestamp, float] = {}
        if not act_df.empty:
            act_map = act_df.set_index("start_time")["generation_mw"].to_dict()

        for _, row in selected.iterrows():
            st_ts = pd.Timestamp(row["start_time"])
            fc_mw = (
                float(row["forecast_mw"])
                if row["has_forecast"] and pd.notna(row["forecast_mw"])
                else None
            )
            act_mw = act_map.get(st_ts)

            if fc_mw is None:
                n_missing_fc += 1
            if act_mw is None:
                n_missing_act += 1

            err_mw = (fc_mw - act_mw) if (fc_mw is not None and act_mw is not None) else None

            cutoff_slots.append(
                {
                    "start_time": st_ts,
                    "forecast_mw": fc_mw,
                    "actual_mw": act_mw,
                    "error_mw": err_mw,
                    "horizon_h": float(row["horizon_h"])
                    if pd.notna(row.get("horizon_h"))
                    else None,
                }
            )

        curr += timedelta(days=1)

    cutoff_df = pd.DataFrame(cutoff_slots)

    if not cutoff_df.empty:
        err_series = cutoff_df["error_mw"]
        act_series = cutoff_df["actual_mw"]
        kpi_dict = compute_all_kpis(err_series, act_series)
    else:
        kpi_dict = {
            "mae": None,
            "rmse": None,
            "bias": None,
            "wmape": None,
            "n": 0,
            "p50_abs_error": None,
            "p90_abs_error": None,
            "p95_abs_error": None,
            "signed_p5": None,
            "signed_p10": None,
            "signed_p50": None,
            "signed_p90": None,
            "signed_p95": None,
        }

    kpis = KpiSchema(
        mae=round(kpi_dict["mae"], 1) if kpi_dict.get("mae") is not None else None,
        rmse=round(kpi_dict["rmse"], 1) if kpi_dict.get("rmse") is not None else None,
        bias=round(kpi_dict["bias"], 1) if kpi_dict.get("bias") is not None else None,
        wmape=round(kpi_dict["wmape"], 4) if kpi_dict.get("wmape") is not None else None,
        n=kpi_dict.get("n", 0),
        p50_abs_error=round(kpi_dict["p50_abs_error"], 1)
        if kpi_dict.get("p50_abs_error") is not None
        else None,
        p90_abs_error=round(kpi_dict["p90_abs_error"], 1)
        if kpi_dict.get("p90_abs_error") is not None
        else None,
        p95_abs_error=round(kpi_dict["p95_abs_error"], 1)
        if kpi_dict.get("p95_abs_error") is not None
        else None,
        signed_p5=round(kpi_dict["signed_p5"], 1)
        if kpi_dict.get("signed_p5") is not None
        else None,
        signed_p10=round(kpi_dict["signed_p10"], 1)
        if kpi_dict.get("signed_p10") is not None
        else None,
        signed_p50=round(kpi_dict["signed_p50"], 1)
        if kpi_dict.get("signed_p50") is not None
        else None,
        signed_p90=round(kpi_dict["signed_p90"], 1)
        if kpi_dict.get("signed_p90") is not None
        else None,
        signed_p95=round(kpi_dict["signed_p95"], 1)
        if kpi_dict.get("signed_p95") is not None
        else None,
        n_missing_forecast=n_missing_fc,
        n_missing_actual=n_missing_act,
    )

    by_hour_raw = metrics_by_hour(cutoff_df) if not cutoff_df.empty else []
    by_day_raw = metrics_by_day(cutoff_df) if not cutoff_df.empty else []

    # Horizon breakdown uses ALL paired forecasts/actuals across the delivery window
    all_pairs_df = _build_all_forecast_actual_pairs(repo, start_decision, end_decision)
    by_horizon_raw = metrics_by_horizon(all_pairs_df) if not all_pairs_df.empty else []

    return MetricsResponse(
        start_date=start_decision,
        end_date=end_decision,
        cutoff=cutoff_hhmm,
        kpis=kpis,
        by_hour=[HourRow(**r) for r in by_hour_raw],
        by_horizon=[HorizonRow(**r) for r in by_horizon_raw],
        by_day=[DayRow(**r) for r in by_day_raw],
    )


def _build_all_forecast_actual_pairs(
    repo: DataRepository,
    start_decision: date,
    end_decision: date,
) -> pd.DataFrame:
    """Build paired DataFrame of all WINDFOR rows matched to FUELHH actuals."""
    del_start = pd.Timestamp(delivery_date_from_decision(start_decision), tz="UTC")
    del_end = pd.Timestamp(delivery_date_from_decision(end_decision), tz="UTC") + pd.Timedelta(
        days=1
    )

    fcs = repo.forecasts_for_range(del_start, del_end)
    acts = repo.actuals_for_range(del_start, del_end)

    if fcs.empty or acts.empty:
        return pd.DataFrame(columns=["horizon_h", "error_mw"])

    merged = fcs.merge(
        acts[["start_time", "generation_mw"]].rename(columns={"generation_mw": "actual_mw"}),
        on="start_time",
        how="inner",
    )
    merged["error_mw"] = merged["forecast_mw"] - merged["actual_mw"]
    merged["horizon_h"] = (
        merged["start_time"] - merged["publish_time"]
    ).dt.total_seconds() / 3600.0
    return merged[["horizon_h", "error_mw"]].dropna()
