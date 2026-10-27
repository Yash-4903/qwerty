# Video Walkthrough Script (Total Duration &le; 10 Minutes)

This script is divided into two distinct parts:
1. **Part 1: Customer & Trader Pitch (&le; 5 min)** — Business focus, decision workflow, financial risk protection.
2. **Part 2: Technical Architecture Review (&le; 5 min)** — System architecture, domain algorithms, testing, and production engineering.

---

## Part 1: Customer & Trader Pitch (Business Focus &le; 5 Minutes)

### 0:00 – 0:45 | The Commercial Problem
> *"Good morning. If you work on a UK day-ahead power trading desk, you face the same high-stakes decision every single morning before 11:00 AM London time:*
> 
> *You have to commit to buying tomorrow's electricity today. In the UK, wind power provides a huge portion of generation, but it fluctuates dramatically. If you trust an over-optimistic wind forecast and under-buy baseline power, you're forced to cover the shortfall on the prompt market or in the Balancing Mechanism at cash-out prices that can exceed £200 or £300/MWh. Conversely, if you under-trust wind and over-buy thermal generation, you waste capital.*
> 
> *Our team built the **UK Wind Forecast Decision Dashboard** to solve this exact problem: telling your desk what wind forecast is actually available the moment you make the decision, and sizing an exact, quantified safety margin so you never get caught short."*

### 0:45 – 2:00 | Workflow Demo: Decision Day 15 Jan &rarr; Delivery 16 Jan
> *[Action: On the dashboard, point to the Decision Date Picker set to 15 Jan 2026, Cutoff 09:00 London]*
> 
> *"Let's look at the workflow. Here, our trader is making their procurement decision on **15 January 2026**. Gate closure is at 11:00, so our cutoff is set to **09:00 London time**.*
> 
> *Notice what the dashboard immediately delivers at the top of the screen:*
> 
> 1. *Target Delivery Day: Automatically identifies delivery for **16 January 2026**.*
> 2. *Expected Wind Generation: An average of **7,930 MW** across the day, peaking at **10,375 MW** and troughing at **6,242 MW**.*
> 3. *And right here in the primary callout: **Suggested Shortfall Buffer: 4,311 MW**.*
> 
> *The system analyzed historical forecast errors up to this date and determined that 90% of the time, actual wind generation came within 4,311 MW of the forecast. This gives the trading desk an empirical, defensible buffer of backup thermal capacity to procure."*

### 2:00 – 3:30 | The Main Chart & Quantified Uncertainty
> *[Action: Scroll to the main Forecast vs Actual envelope chart, hover over peaks and troughs]*
> 
> *"Looking at the main chart:*
> 
> - *The **solid blue line** represents the latest wind generation forecast published before our 09:00 cutoff.*
> - *The **shaded envelope** shows our empirical 90% confidence uncertainty band.*
> - *The **green dashed line** shows what actually happened on the delivery day.*
> 
> *Hovering over any half-hour shows the publication timestamp and lead horizon. For instance, in the afternoon peak, the forecast was published 15.5 hours ahead. The trader can clearly see whether actual generation stayed within the safety envelope. This replaces gut-feel with quantified confidence intervals."*

### 3:30 – 4:30 | Accuracy Benchmarks Across January 2026
> *[Action: Point to the Month-to-Date KPI grid]*
> 
> *"Across January 2026 as a whole, what does the historical track record show?*
> 
> - *Our **Mean Absolute Error (MAE)** is **2,022.5 MW**.*
> - *Our **Weighted Mean Absolute Percentage Error (wMAPE)** is **17.92%**.*
> - *Notice our **Forecast Bias is +1,745.9 MW**. This is crucial: the national forecast in January exhibited a systematic over-forecasting bias. Knowing this bias exists is worth millions of pounds to a trading desk because it warns the trader that wind is more likely to fall short than exceed expectations.*
> - *Our **P90 Absolute Error** sits at **4,154.4 MW**."*

### 4:30 – 5:00 | Business Value & Next Steps
> *"In summary, this dashboard transforms raw Elexon BMRS data into clear, actionable procurement advice before gate closure every morning. It directly minimizes imbalance penalty exposure while avoiding costly over-hedging.*
> 
> *In production, this pilot can be extended to 12 months of historical data, incorporate regional offshore/onshore breakdowns, and integrate prompt intraday re-forecasting. Thank you."*

---

## Part 2: Technical Architecture & Implementation (Tech Lead &le; 5 Minutes)

### 0:00 – 1:00 | System Architecture & Zero-API Runtime Dependency
> *[Action: Open docs/ARCHITECTURE.md and mermaid diagram]*
> 
> *"Hello. Now let's dive into the technical architecture.*
> 
> *The project is engineered as a clean, production-grade monorepo containing a Python FastAPI backend and a React 18 TypeScript frontend.*
> 
> *One of our most important design decisions was **zero runtime dependency on external APIs**. In `app/ingestion/`, our `ElexonClient` fetches public BMRS datasets (`FUELHH` actuals and `WINDFOR` forecasts) using 48-hour chunking and exponential backoff retry. During build or ingestion, data is validated, deduplicated, and serialized into high-performance Apache Parquet files (`actuals.parquet` and `forecasts.parquet`).*
> 
> *At application startup, our `DataRepository` loads these parquet files once into memory. As a result, all API endpoints respond in under **20 milliseconds** with deterministic predictability."*

### 1:00 – 2:00 | Core Domain Logic & Cutoff Selection
> *[Action: Open backend/app/domain/cutoff.py and tests/unit/test_cutoff.py]*
> 
> *"Let's look at the core domain logic in `app/domain/cutoff.py`. This is written as pure, framework-free Python without any HTTP or database dependencies.*
> 
> *For any delivery day $D$, the decision cutoff is evaluated at day $D-1$ at time $HH:MM$. We handle timezones strictly in UTC internally while converting to `Europe/London` via standard library `zoneinfo`. This guarantees full correctness across both GMT winter and BST summer daylight savings.*
> 
> *For each of the 48 delivery half-hours, `select_latest_forecast_at_cutoff()` identifies all candidates published on or before the cutoff timestamp ($publishTime \le cutoff$), sorting deterministically by publication time and selecting the latest forecast.*
> 
> *If no forecast was published prior to cutoff, the slot is explicitly marked with `has_forecast: false` and surfaced to the UI. We **never** silently forward-fill or impute missing data."*

### 2:00 – 3:00 | Preventing Look-Ahead Leakage & Metric Rigor
> *[Action: Open backend/app/domain/metrics.py and backend/app/services/forecast_service.py]*
> 
> *"A frequent trap in energy analytics is look-ahead leakage. In `forecast_service.py`, when computing the shortfall buffer and prediction band for a decision date $D-1$, the historical signed error quantiles are calculated **strictly from decision days prior to $D-1$**.*
> 
> *Regarding metrics:*
> - *We compute **wMAPE = $\frac{\sum |Error|}{\sum Actual}$**. We intentionally avoided standard MAPE because actual wind output can drop near zero, which causes standard MAPE to explode to thousands of percent.*
> - *Our error definition is strictly **Error = Forecast − Actual**. Positive error represents an over-forecast (shortfall risk), which directly drives our P90 buffer calculation.*
> - *Our accuracy diagnostics tabs break down errors by hour of day (0–23), lead horizon (0–6h, 6–12h, etc.), and daily trend."*

### 3:00 – 4:00 | Automated Testing & Quality Gates
> *[Action: Show terminal running `pytest tests/ -v` and `mypy app/`]*
> 
> *"Quality gates are enforced across both stacks:*
> 
> - *We have **34 automated pytest tests** covering unit cutoff edge cases (exact equality boundaries, post-cutoff exclusions, ties), pure metrics math against hand-computed fixtures, and integration tests across every API endpoint.*
> - *Our backend domain coverage exceeds **88%**.*
> - *The backend is fully typed and passes `mypy --strict` with zero issues, alongside `ruff` linting and formatting.*
> - *The frontend is built with strict TypeScript, Vite, TanStack Query, and Tailwind CSS, compiling with zero type errors.*
> - *Our GitHub Actions CI workflow in `.github/workflows/ci.yml` runs linting, formatting, type checking, test suites, and Docker container builds on every push."*

### 4:00 – 5:00 | Containerization & Deployment
> *[Action: Open Dockerfile and docker-compose.prod.yml]*
> 
> *"Finally, deployment is designed for single-container cloud hosting on platforms like Heroku (via container stack), Render, or Docker Compose.*
> 
> *Our multi-stage `Dockerfile`:*
> 1. *Stage 1 builds the optimized React frontend bundle via Node 20.*
> 2. *Stage 2 prepares Python 3.12 dependencies using `uv`.*
> 3. *Stage 3 creates a slim, non-root runner container that embeds the pre-baked Parquet data and static UI assets. FastAPI serves both the `/api/v1` routes and the static single-page application from a unified port, respecting dynamic `$PORT` environment variables and including Docker `HEALTHCHECK` monitoring.*
> 
> *All assumptions and empirical findings are documented in `docs/ASSUMPTIONS.md` and `docs/DATA_NOTES.md`. Thank you."*
