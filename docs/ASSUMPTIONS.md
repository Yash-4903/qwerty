# Technical Assumptions & Methodology Record

This document records the design choices, domain definitions, and assumptions implemented across the application.

---

## 1. Decision Cutoff Rationale & Configuration

- **Default Cutoff:** `09:00 Europe/London` on day `D-1`.
- **Market Context:** Great Britain day-ahead wholesale electricity auctions (N2EX and EPEX Spot) close at 11:00 London time on D-1. Setting the decision cutoff at 09:00 provides power buyers with a realistic, actionable 2-hour window to review the latest forecasts, evaluate generation risks, and execute bids.
- **Configurability:** The cutoff is fully configurable via the UI dropdown, the REST API `cutoff=HH:MM` query parameter, and the `DEFAULT_CUTOFF_TIME` environment variable.
- **Timezone Handling:** Internally, all calculations and timestamps are stored in UTC. London time is converted using Python's standard `zoneinfo.ZoneInfo("Europe/London")`, correctly handling Greenwich Mean Time (GMT) in winter and British Summer Time (BST) in summer.

---

## 2. Data Window Convention

- **Decision Dates ($D-1$):** `2026-01-01` to `2026-01-31` (all days in January 2026).
- **Delivery Days ($D = D-1 + 1$):** `2026-01-02` to `2026-02-01`.
- **Historical Ingestion Scope:**
  - Actual generation (`FUELHH` with `fuelType == "WIND"`) covers delivery days from `2026-01-02` through `2026-02-01`.
  - Forecasts (`WINDFOR`) were pulled from publication date `2025-12-24` through `2026-02-02`, providing up to 7+ days of lead horizon for early January delivery slots.

---

## 3. Error Sign Convention & Risk Interpretation

- **Definition:**
  $$\text{Error} = \text{Forecast} - \text{Actual} \quad (\text{MW})$$
- **Positive Error ($\text{Error} > 0$):**
  - **Over-forecast.** Wind generated was lower than predicted.
  - **Commercial Impact:** The buyer experiences an unexpected energy **shortfall** and is exposed to volatile prompt or System Buy Prices (cash-out) in the balancing mechanism. This represents the primary downside risk.
- **Negative Error ($\text{Error} < 0$):**
  - **Under-forecast.** Wind generated was higher than predicted.
  - **Commercial Impact:** The buyer has surplus generation and sells into balancing (spill risk), typically incurring smaller opportunity costs.

---

## 4. Percentage Error Metric: wMAPE vs MAPE

- We compute **Weighted Mean Absolute Percentage Error (wMAPE)**:
  $$\text{wMAPE} = \frac{\sum |\text{Forecast} - \text{Actual}|}{\sum \text{Actual}}$$
- **Why not standard MAPE?**
  $$\text{MAPE} = \frac{1}{n} \sum \frac{|\text{Forecast} - \text{Actual}|}{\text{Actual}}$$
  During low-wind periods or calm spells, actual wind generation can approach zero. Standard MAPE divides by near-zero numbers, causing individual half-hours to explode to 5,000%+ errors. wMAPE normalizes total absolute errors against total generation volume, providing a reliable measure for procurement portfolios.

---

## 5. Decision Support & Shortfall Buffer

- **Shortfall Buffer (MW):** Derived as the **90th percentile of positive signed errors** ($P_{90}$):
  $$\text{Buffer} = \text{Quantile}_{0.90}(\{\text{Forecast} - \text{Actual} \mid \text{historical slots}\})$$
  This answers the trader's fundamental question: *"How much backup thermal/peaker capacity must I reserve so that I am covered 90% of the time against wind shortfalls?"*
- **Uncertainty Band:**
  $$\text{Band Low} = \max(0, \text{Forecast} - \max(0, P_{90}))$$
  $$\text{Band High} = \text{Forecast} - \min(0, P_{10})$$
- **Strict Prevention of Look-Ahead Leakage:**
  - When evaluating decision date $D-1$, the historical error distribution is calculated **only** from decision days strictly prior to $D-1$.
  - When fewer than 3 prior days exist (e.g. 1–3 Jan 2026), the system falls back to the full-month quantile benchmark and explicitly flags `band_source: "full_month_fallback"`.

---

## 6. Data Integrity & Missing Values

- Half-hourly slots for which no forecast had been published on or before the cutoff are marked `has_forecast = False` with `forecast_mw = null`.
- Missing values are explicitly counted and surfaced in the API and UI; they are never silently forward-filled or imputed.
- Duplicate records matching `start_time` and `publish_time` retain the latest entry.
