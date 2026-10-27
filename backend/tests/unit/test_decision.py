from __future__ import annotations

import pandas as pd

from app.domain.decision import compute_decision_output, compute_uncertainty_band


class TestDecisionLogic:
    def test_uncertainty_band_calculation(self):
        # Forecast: 10,000 MW.
        # Historical signed error: q90 = +1,200 MW (over-forecast risk), q10 = -800 MW (under-forecast)
        quantiles = {"signed_p90": 1200.0, "signed_p10": -800.0}
        band_low, band_high = compute_uncertainty_band(10000.0, quantiles)

        # band_low = 10000 - 1200 = 8800 MW (shortfall protection bound)
        assert band_low == 8800.0
        # band_high = 10000 - (-800) = 10800 MW (upper wind generation bound)
        assert band_high == 10800.0

    def test_positive_error_is_shortfall_risk(self):
        """Positive error = forecast > actual = shortfall risk the buyer must cover."""
        quantiles = {"signed_p90": 1500.0, "signed_p10": -500.0}
        fc_series = pd.Series([5000.0, 6000.0, 7000.0])
        decision = compute_decision_output(fc_series, quantiles, n_history_slots=48)

        assert decision["shortfall_buffer_mw"] == 1500.0
        assert "1,500 MW" in decision["summary"]
        assert decision["avg_forecast_mw"] == 6000.0

    def test_empty_forecast_series(self):
        empty_fc = pd.Series([], dtype=float)
        decision = compute_decision_output(empty_fc, {}, n_history_slots=0)
        assert decision["avg_forecast_mw"] is None
        assert "No forecast data available" in decision["summary"]
