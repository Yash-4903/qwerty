from __future__ import annotations

import math

import pandas as pd
import pytest

from app.domain.metrics import (
    abs_error_quantiles,
    bias,
    compute_all_kpis,
    mae,
    metrics_by_day,
    metrics_by_horizon,
    metrics_by_hour,
    rmse,
    signed_error_quantiles,
    wmape,
)


class TestMetricsPureFunctions:
    def test_mae_known_values(self):
        errs = pd.Series([100.0, -200.0, 50.0])
        # (|100| + |-200| + |50|) / 3 = 350 / 3 = 116.666...
        assert mae(errs) == pytest.approx(116.6666667)

    def test_rmse_known_values(self):
        errs = pd.Series([30.0, -40.0])
        # sqrt((900 + 1600) / 2) = sqrt(1250) = 35.3553...
        assert rmse(errs) == pytest.approx(math.sqrt(1250.0))

    def test_bias_known_values(self):
        errs = pd.Series([150.0, -50.0, 20.0])
        # (150 - 50 + 20) / 3 = 120 / 3 = 40.0
        assert bias(errs) == pytest.approx(40.0)

    def test_wmape_known_values(self):
        errs = pd.Series([100.0, -200.0])
        acts = pd.Series([1000.0, 3000.0])
        # sum(|err|) = 300; sum(act) = 4000; wmape = 300 / 4000 = 0.075 (7.5%)
        assert wmape(errs, acts) == pytest.approx(0.075)

    def test_wmape_zero_actual_handling(self):
        errs = pd.Series([50.0])
        acts = pd.Series([0.0])
        assert wmape(errs, acts) is None

    def test_empty_series_handling(self):
        empty = pd.Series([], dtype=float)
        assert mae(empty) is None
        assert rmse(empty) is None
        assert bias(empty) is None
        assert wmape(empty, empty) is None

    def test_abs_and_signed_quantiles(self):
        # Errors: -200, -100, 0, 100, 200
        errs = pd.Series([-200.0, -100.0, 0.0, 100.0, 200.0])
        signed_q = signed_error_quantiles(errs, [0.10, 0.50, 0.90])
        assert signed_q["p50"] == pytest.approx(0.0)
        assert signed_q["p10"] < 0
        assert signed_q["p90"] > 0

        abs_q = abs_error_quantiles(errs, [0.50])
        # Absolute errors: 0, 100, 100, 200, 200 -> median is 100
        assert abs_q["p50"] == pytest.approx(100.0)

    def test_compute_all_kpis_integration(self):
        errs = pd.Series([150.0, -20.0, 50.0])
        acts = pd.Series([950.0, 820.0, 700.0])
        kpis = compute_all_kpis(errs, acts)
        assert kpis["n"] == 3
        assert kpis["mae"] == pytest.approx((150 + 20 + 50) / 3)
        assert kpis["bias"] == pytest.approx((150 - 20 + 50) / 3)
        assert kpis["wmape"] == pytest.approx(220.0 / 2470.0)


class TestMetricsBreakdowns:
    def test_metrics_by_hour(self):
        df = pd.DataFrame(
            {
                "start_time": pd.to_datetime(
                    ["2026-01-15T00:00:00Z", "2026-01-15T00:30:00Z", "2026-01-15T01:00:00Z"]
                ),
                "error_mw": [100.0, -50.0, 200.0],
            }
        )
        res = metrics_by_hour(df)
        assert len(res) == 2
        h0 = [r for r in res if r["hour"] == 0][0]
        assert h0["n"] == 2
        assert h0["mae"] == pytest.approx(75.0)

    def test_metrics_by_horizon(self):
        df = pd.DataFrame(
            {
                "horizon_h": [3.0, 5.5, 14.0, 30.0],
                "error_mw": [10.0, 20.0, 100.0, 300.0],
            }
        )
        res = metrics_by_horizon(df)
        b0_6 = [r for r in res if r["bucket"] == "0-6h"][0]
        assert b0_6["n"] == 2
        assert b0_6["mae"] == pytest.approx(15.0)

        b12_24 = [r for r in res if r["bucket"] == "12-24h"][0]
        assert b12_24["n"] == 1
        assert b12_24["mae"] == pytest.approx(100.0)

    def test_metrics_by_day(self):
        df = pd.DataFrame(
            {
                "start_time": pd.to_datetime(
                    ["2026-01-15T00:00:00Z", "2026-01-15T12:00:00Z", "2026-01-16T00:00:00Z"]
                ),
                "error_mw": [100.0, -100.0, 50.0],
            }
        )
        res = metrics_by_day(df)
        assert len(res) == 2
        d15 = [r for r in res if r["date"] == "2026-01-15"][0]
        assert d15["n"] == 2
        assert d15["mae"] == pytest.approx(100.0)
        assert d15["bias"] == pytest.approx(0.0)
