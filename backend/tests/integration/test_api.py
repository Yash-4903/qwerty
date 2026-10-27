from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(sample_repo):
    with TestClient(app) as test_client:
        yield test_client


class TestSystemEndpoints:
    def test_health_check_loaded(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["data_loaded"] is True
        assert data["actuals_rows"] > 0
        assert data["forecast_rows"] > 0


class TestMetadataEndpoint:
    def test_meta_endpoint(self, client):
        resp = client.get("/api/v1/meta")
        assert resp.status_code == 200
        data = resp.json()
        assert data["min_decision_date"] == "2026-01-01"
        assert data["max_decision_date"] == "2026-01-31"
        assert data["default_cutoff"] == "09:00"
        assert "Europe/London" in data["timezone"]


class TestForecastEndpoint:
    def test_valid_decision_date(self, client):
        # 2026-01-14 decision date -> 2026-01-15 delivery date
        resp = client.get("/api/v1/forecast?decision_date=2026-01-14&cutoff=09:00")
        assert resp.status_code == 200
        data = resp.json()
        assert data["decision_date"] == "2026-01-14"
        assert data["delivery_date"] == "2026-01-15"
        assert len(data["slots"]) == 48
        assert "decision" in data
        assert data["total_slots"] == 48

    def test_date_out_of_range(self, client):
        resp = client.get("/api/v1/forecast?decision_date=2025-12-31")
        assert resp.status_code == 400
        data = resp.json()
        assert "between" in data["error"]["message"]

    def test_invalid_cutoff_format(self, client):
        resp = client.get("/api/v1/forecast?decision_date=2026-01-14&cutoff=invalid")
        assert resp.status_code == 422
        data = resp.json()
        assert "Cutoff must be in format HH:MM" in data["error"]["message"]


class TestMetricsEndpoint:
    def test_valid_metrics(self, client):
        resp = client.get("/api/v1/metrics?start=2026-01-14&end=2026-01-15&cutoff=09:00")
        assert resp.status_code == 200
        data = resp.json()
        assert "kpis" in data
        assert "by_hour" in data
        assert "by_horizon" in data
        assert "by_day" in data

    def test_invalid_date_order(self, client):
        resp = client.get("/api/v1/metrics?start=2026-01-20&end=2026-01-10")
        assert resp.status_code == 400


class TestCsvExportEndpoint:
    def test_csv_export(self, client):
        resp = client.get("/api/v1/export.csv?start=2026-01-14&end=2026-01-14&cutoff=09:00")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert "attachment" in resp.headers["content-disposition"]
        content = resp.text
        lines = content.strip().split("\r\n") if "\r\n" in content else content.strip().split("\n")
        assert len(lines) >= 49  # 1 header + 48 half-hour slots
        assert "start_time_utc" in lines[0]
        assert "forecast_mw" in lines[0]
