# REST API Reference (`/api/v1`)

Interactive OpenAPI documentation is available locally at `http://localhost:8000/docs` or `https://<deployed-url>/docs`.

All response payloads use JSON with ISO 8601 UTC timestamps. Error responses adhere to the standard envelope `{ "error": { "code": string, "message": string } }`.

---

## 1. System Endpoints

### `GET /health`
Liveness check and dataset load status.

**Response (200 OK):**
```json
{
  "status": "ok",
  "data_loaded": true,
  "actuals_rows": 1489,
  "forecast_rows": 23360
}
```

---

## 2. Metadata

### `GET /api/v1/meta`
Returns application operational parameters, decision date limits, default cutoffs, and data coverage.

**Response (200 OK):**
```json
{
  "min_decision_date": "2026-01-01",
  "max_decision_date": "2026-01-31",
  "default_cutoff": "09:00",
  "timezone": "Europe/London",
  "data_coverage_start": "2026-01-01T23:30:00+00:00",
  "data_coverage_end": "2026-02-01T23:30:00+00:00",
  "assumptions_summary": "Decision date D-1 is in January 2026. Delivery date D is D-1 + 1 day...",
  "last_data_refresh": "Elexon BMRS January 2026"
}
```

---

## 3. Forecast & Decision Support

### `GET /api/v1/forecast`
Returns the 48 half-hourly delivery day slots and decision guidance for a given decision date and cutoff time.

**Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `decision_date` | `YYYY-MM-DD` | Yes | Decision date $D-1$ (restricted to `2026-01-01` to `2026-01-31`) |
| `cutoff` | `HH:MM` | No | Europe/London cutoff time on $D-1$ (default: `09:00`) |

**Sample Request:**
```http
GET /api/v1/forecast?decision_date=2026-01-15&cutoff=09:00
```

**Response (200 OK):**
```json
{
  "decision_date": "2026-01-15",
  "delivery_date": "2026-01-16",
  "cutoff_utc": "2026-01-15T09:00:00Z",
  "cutoff_london": "09:00 GMT",
  "slots": [
    {
      "start_time": "2026-01-16T00:00:00Z",
      "forecast_mw": 8420.0,
      "actual_mw": 8110.0,
      "error_mw": 310.0,
      "publish_time": "2026-01-15T08:30:00Z",
      "horizon_h": 15.5,
      "band_low": 4109.0,
      "band_high": 9220.0,
      "has_forecast": true
    }
  ],
  "n_missing_forecast": 0,
  "n_missing_actual": 0,
  "total_slots": 48,
  "decision": {
    "avg_forecast_mw": 7930.0,
    "peak_forecast_mw": 10375.0,
    "trough_forecast_mw": 6242.0,
    "shortfall_buffer_mw": 4311.0,
    "summary": "Forecast wind generation averages 7,930 MW across the delivery day...",
    "n_history_slots": 336,
    "band_source": "prior_dates"
  }
}
```

---

## 4. Aggregated Metrics & Diagnostics

### `GET /api/v1/metrics`
Returns month-to-date summary KPIs and breakdowns by hour, forecast lead horizon, and day.

**Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `start` | `YYYY-MM-DD` | No | Start decision date (default: `2026-01-01`) |
| `end` | `YYYY-MM-DD` | No | End decision date (default: `2026-01-31`) |
| `cutoff` | `HH:MM` | No | Europe/London cutoff time (default: `09:00`) |

**Sample Request:**
```http
GET /api/v1/metrics?start=2026-01-01&end=2026-01-31&cutoff=09:00
```

**Response (200 OK):**
```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-31",
  "cutoff": "09:00",
  "kpis": {
    "mae": 2022.5,
    "rmse": 2497.4,
    "bias": 1745.9,
    "wmape": 0.1792,
    "n": 744,
    "p50_abs_error": 1750.0,
    "p90_abs_error": 4154.4,
    "p95_abs_error": 4890.2,
    "signed_p5": -620.0,
    "signed_p10": -210.0,
    "signed_p50": 1640.0,
    "signed_p90": 4154.4,
    "signed_p95": 4890.2,
    "n_missing_forecast": 744,
    "n_missing_actual": 0
  },
  "by_hour": [...],
  "by_horizon": [...],
  "by_day": [...]
}
```

---

## 5. CSV Data Export

### `GET /api/v1/export.csv`
Streams a downloadable CSV containing half-hourly slot records with forecasts, actuals, error, and horizon.

**Query Parameters:**
`start`, `end`, `cutoff` (same as `/metrics`).

**Sample Response Header:**
```http
HTTP/1.1 200 OK
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="wind_forecast_export_2026-01-01_to_2026-01-31.csv"
```
