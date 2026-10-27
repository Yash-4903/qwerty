from __future__ import annotations

from datetime import date, datetime, timezone

import pandas as pd
import pytest

from app.domain.cutoff import (
    decision_date_to_cutoff_utc,
    delivery_date_from_decision,
    generate_expected_half_hours,
    parse_cutoff_time,
    select_latest_forecast_at_cutoff,
)
from tests.fixtures.sample_data import get_sample_forecasts_df

UTC = timezone.utc


class TestCutoffParsing:
    def test_valid_times(self):
        assert parse_cutoff_time("09:00") == (9, 0)
        assert parse_cutoff_time("00:00") == (0, 0)
        assert parse_cutoff_time("23:59") == (23, 59)
        assert parse_cutoff_time("12:30") == (12, 30)

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="HH:MM"):
            parse_cutoff_time("9:00")
        with pytest.raises(ValueError, match="HH:MM"):
            parse_cutoff_time("09:0")
        with pytest.raises(ValueError, match="HH:MM"):
            parse_cutoff_time("09-00")
        with pytest.raises(ValueError, match="HH:MM"):
            parse_cutoff_time("invalid")

    def test_invalid_range(self):
        with pytest.raises(ValueError, match="out of range"):
            parse_cutoff_time("24:00")
        with pytest.raises(ValueError, match="out of range"):
            parse_cutoff_time("12:60")


class TestTimezoneHandling:
    def test_january_london_is_gmt_utc(self):
        """In January, London is GMT (UTC+0). 09:00 London == 09:00 UTC."""
        d = date(2026, 1, 14)
        cutoff_utc = decision_date_to_cutoff_utc(d, "09:00")
        assert cutoff_utc == datetime(2026, 1, 14, 9, 0, 0, tzinfo=UTC)

    def test_july_london_is_bst_utc_plus_one(self):
        """In July, London is BST (UTC+1). 09:00 London == 08:00 UTC."""
        d = date(2025, 7, 15)
        cutoff_utc = decision_date_to_cutoff_utc(d, "09:00")
        assert cutoff_utc == datetime(2025, 7, 15, 8, 0, 0, tzinfo=UTC)

    def test_delivery_date_is_d_plus_one(self):
        assert delivery_date_from_decision(date(2026, 1, 14)) == date(2026, 1, 15)
        assert delivery_date_from_decision(date(2026, 1, 31)) == date(2026, 2, 1)

    def test_generate_expected_half_hours(self):
        slots = generate_expected_half_hours(date(2026, 1, 15))
        assert len(slots) == 48
        assert slots[0] == datetime(2026, 1, 15, 0, 0, 0, tzinfo=UTC)
        assert slots[-1] == datetime(2026, 1, 15, 23, 30, 0, tzinfo=UTC)


class TestSelectLatestForecastAtCutoff:
    def setup_method(self):
        self.df = get_sample_forecasts_df()
        self.cutoff_utc = datetime(2026, 1, 14, 9, 0, 0, tzinfo=UTC)

    def test_picks_max_publish_time_before_cutoff(self):
        # Slot 00:00 has forecasts at 07:00 (1000MW), 08:30 (1100MW), 09:30 (1200MW)
        # At cutoff 09:00, max publish_time <= 09:00 is 08:30 (1100MW)
        res = select_latest_forecast_at_cutoff(self.df, self.cutoff_utc)
        slot0 = res[res["start_time"] == pd.Timestamp("2026-01-15T00:00:00Z")].iloc[0]
        assert slot0["forecast_mw"] == 1100.0
        assert bool(slot0["has_forecast"]) is True
        assert slot0["publish_time"] == pd.Timestamp("2026-01-14T08:30:00Z")

    def test_excludes_forecast_published_after_cutoff(self):
        # The 1200MW forecast was published at 09:30 and must be excluded
        res = select_latest_forecast_at_cutoff(self.df, self.cutoff_utc)
        slot0 = res[res["start_time"] == pd.Timestamp("2026-01-15T00:00:00Z")].iloc[0]
        assert slot0["forecast_mw"] != 1200.0

    def test_exact_equal_boundary_is_included(self):
        # Slot 00:30 was published exactly at 09:00:00Z
        res = select_latest_forecast_at_cutoff(self.df, self.cutoff_utc)
        slot1 = res[res["start_time"] == pd.Timestamp("2026-01-15T00:30:00Z")].iloc[0]
        assert slot1["forecast_mw"] == 800.0
        assert bool(slot1["has_forecast"]) is True
        assert slot1["publish_time"] == pd.Timestamp("2026-01-14T09:00:00Z")

    def test_slot_with_no_eligible_forecast(self):
        # Slot 01:00 only had a forecast published at 10:00:00Z (after cutoff)
        res = select_latest_forecast_at_cutoff(self.df, self.cutoff_utc)
        slot2 = res[res["start_time"] == pd.Timestamp("2026-01-15T01:00:00Z")].iloc[0]
        assert bool(slot2["has_forecast"]) is False
        assert pd.isna(slot2["forecast_mw"])
        assert pd.isna(slot2["publish_time"])

    def test_deterministic_tie_breaker(self):
        # Slot 01:30 has two forecasts at 06:00:00Z (750MW and 700MW)
        res = select_latest_forecast_at_cutoff(self.df, self.cutoff_utc)
        slot3 = res[res["start_time"] == pd.Timestamp("2026-01-15T01:30:00Z")].iloc[0]
        assert bool(slot3["has_forecast"]) is True
        assert slot3["forecast_mw"] == 750.0  # sorted descending by forecast_mw
