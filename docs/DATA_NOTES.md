# DATA_NOTES.md — Elexon BMRS Data Quality Report

**Generated:** 2026-10-27 15:44:25 UTC  
**Source:** Elexon Insights Solution (BMRS) API (`https://data.elexon.co.uk/bmrs/api/v1`)  

---

## 1. FUELHH Actuals (Wind Only)

- **Total Rows:** 1,489
- **Unique 30-min Slots:** 1,489
- **Start Time Range:** 2026-01-01T23:30:00+00:00 to 2026-02-01T23:30:00+00:00
- **Null Generation Values:** 0
- **Negative Generation Values:** 0
- **Generation Range:** 1,695.0 MW to 17,805.0 MW (mean: 11,286.4 MW)
- **Integrity Check:** UK January national wind generation typically ranges between hundreds of MW up to ~22,000 MW. The empirical numbers align with physical expectations.

---

## 2. WINDFOR Forecasts

- **Total Rows:** 23,360
- **Unique Delivery Slots:** 1,009
- **Delivery Slot Range:** 2025-12-23T21:00:00+00:00 to 2026-02-03T21:00:00+00:00
- **Publication Time Range:** 2025-12-24T02:30:00+00:00 to 2026-02-01T22:30:00+00:00
- **Forecasts Per Slot:** min=8, max=32, mean=23.2
- **Horizon Range:** -25.5h to 66.5h ahead
- **Null Forecast Values:** 0
- **Negative Forecast Values:** 0
- **Forecast Range:** 1,981.0 MW to 21,353.0 MW (mean: 12,302.4 MW)

---

## 3. Empirical Observations & Normalization Decisions

- **Resolution:** Confirmed 30-minute intervals (`startTime` increments every 30 minutes).
- **Timezones:** All timestamps returned in ISO 8601 UTC (`Z`). All internal storage and calculation standardizes to UTC.
- **Duplicates:** Exact duplicate records removed; on identical `start_time` and `publish_time`, the latest record is retained.
- **Missing Slots:** Filtered and tracked explicitly; no forward-filling or synthetic interpolation is performed.
