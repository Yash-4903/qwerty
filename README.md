# UK Wind Forecast Decision Dashboard

A specialized day-ahead decision support web application built for UK electricity utility trading desks. When buying tomorrow's power before gate closure, power buyers need to know the latest wind generation forecast available at the decision cutoff and quantitatively evaluate historical accuracy to size an optimal safety buffer. This dashboard provides empirical risk bands, shortfall buffer recommendations, and accuracy diagnostics powered by public Elexon BMRS data for January 2026.

---

## Live Demo & Documentation

- **Live Application:** `https://wind-dashboard-pilot.herokuapp.com` *(or local run via Docker)*
- **Interactive OpenAPI Documentation:** Available at `/docs` when running the application.
- **Video Walkthrough Script:** [`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md) contains the timed 5-minute customer pitch and 5-minute tech lead review with real empirical numbers.

---

## AI Usage Disclosure

In compliance with project specifications, this application was engineered with the assistance of **AI coding agents (Antigravity / Claude / Gemini)**. The AI tool assisted in generating project scaffolding, boilerplate API routing, schema typing, and frontend component layout. All core domain logic (cutoff selection algorithms, timezone conversions, metric formulations, look-ahead leakage prevention, and data validation rules) were directed, verified, and audited by the engineer against energy domain standards.

---

## Repository Structure

```
.
├── AGENT.md                  # Project brief and engineering specification (gitignored)
├── README.md                 # Product overview, setup guide, and documentation
├── Dockerfile                # Multi-stage production container (builds frontend, serves via FastAPI)
├── docker-compose.yml        # Local development environment (backend + frontend hot-reload)
├── docker-compose.prod.yml   # Production-like single container compose run
├── heroku.yml                # Heroku container stack deployment descriptor
├── Makefile                  # Automation: make dev | run | test | lint | typecheck | ingest
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules (excludes AGENT.md, .venv, node_modules)
├── .dockerignore             # Docker build context exclusions
├── .editorconfig             # Cross-editor formatting specifications
├── .github/workflows/ci.yml  # GitHub Actions CI: lint, format, typecheck, test, Docker build
├── docs/
│   ├── ARCHITECTURE.md       # Architecture overview and component interaction
│   ├── architecture.mmd      # Mermaid source diagram of system architecture
│   ├── ASSUMPTIONS.md        # Technical rationale (cutoff, window, error sign, wMAPE)
│   ├── DATA_NOTES.md         # Empirical data quality report from live Elexon API
│   ├── API.md                # Comprehensive REST API endpoint reference
│   └── VIDEO_SCRIPT.md       # Timed 10-minute video outline with real January 2026 figures
├── data/
│   ├── raw/                  # Raw JSON cached responses from Elexon BMRS API
│   └── processed/            # Committed actuals.parquet and forecasts.parquet
├── backend/
│   ├── pyproject.toml        # Backend configuration, dependencies, ruff, mypy, pytest
│   ├── app/
│   │   ├── main.py           # FastAPI app factory, CORS, static mounting, exception handlers
│   │   ├── core/             # Settings (pydantic-settings), logging, error handling
│   │   ├── api/v1/           # Versioned REST controllers (/forecast, /metrics, /meta, /export.csv)
│   │   ├── schemas/          # Typed Pydantic request & response models
│   │   ├── domain/           # PURE domain algorithms: cutoff.py, metrics.py, decision.py
│   │   ├── services/         # Orchestration layer (forecast_service, metrics_service)
│   │   ├── data/             # In-memory DataRepository loading parquet files
│   │   └── ingestion/        # ElexonClient, validate.py, and fetch_data.py CLI
│   └── tests/
│       ├── fixtures/         # Hand-crafted test fixtures with known mathematical answers
│       ├── unit/             # Unit tests for cutoff, metrics, and decision engines
│       └── integration/      # Integration tests covering all API endpoints
└── frontend/
    ├── package.json          # React 18, TanStack Query/Table, Recharts, Tailwind CSS
    ├── vite.config.ts        # Vite configuration with API proxy
    ├── tsconfig.json         # Strict TypeScript compiler configuration
    ├── tailwind.config.ts    # Tailwind theme and CSS variable setup
    └── src/
        ├── api/              # Typed API client and TanStack Query hooks
        ├── components/
        │   ├── ui/           # Radix UI primitives (Button, Card, Tabs, Dialog, Select, etc.)
        │   ├── layout/       # Header, AssumptionsPanel
        │   ├── controls/     # DecisionDatePicker, CutoffSelect
        │   ├── kpi/          # KpiCard, KpiGrid
        │   ├── charts/       # ForecastVsActualChart, ErrorByHour, Horizon, Distribution, Daily
        │   ├── decision/     # DecisionSummary callout
        │   └── table/        # Paginated, sortable DataTable with CSV download
        ├── lib/              # Formatters, dates (date-fns/date-fns-tz), utils
        ├── pages/            # DashboardPage.tsx
        └── types/            # TypeScript type definitions mirroring backend schemas
```

---

## How to Run

### 1. Docker (Recommended for Production)

Run the single production container serving both the API and the React frontend:

```bash
# Production single-container build & run
docker compose -f docker-compose.prod.yml up --build

# Open http://localhost:8000 in your browser
```

For interactive local development with hot-reload:
```bash
docker compose up --build
# Backend API: http://localhost:8000
# Frontend Dev: http://localhost:5173
```

---

### 2. Local Development Without Docker

#### Backend
```bash
# Set up virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -e "backend[dev]"

# Run FastAPI server
cd backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
# In a separate terminal
cd frontend
npm install
npm run dev

# Open http://localhost:5173
```

---

### 3. Refreshing Data Ingestion Pipeline

To fetch fresh January 2026 actuals and forecasts from Elexon BMRS:

```bash
make ingest
# or:
cd backend && python -m app.ingestion.fetch_data --start 2025-12-24 --end 2026-02-02
```

The script queries `/datasets/FUELHH/stream` and `/datasets/WINDFOR/stream`, validates the dataset, generates `docs/DATA_NOTES.md`, and serializes `actuals.parquet` and `forecasts.parquet` into `data/processed/`.

---

### 4. Running Tests & Quality Gates

```bash
# Run pytest with code coverage (enforces >= 80% coverage)
make test

# Run linter and formatting checks (ruff)
make lint

# Run type checker (mypy and tsc)
make typecheck
```

---

## Key Domain Assumptions

| Parameter | Implemented Rule | Commercial / Domain Rationale |
|---|---|---|
| **Decision Cutoff** | Default `09:00 Europe/London` on $D-1$ | GB day-ahead power auctions close at 11:00 London time; 09:00 provides a 2-hour execution window. |
| **Error Convention** | $\text{Error} = \text{Forecast} - \text{Actual}$ | Positive error = over-forecast = **shortfall risk** requiring backup prompt purchases. |
| **Percentage Error** | $\text{wMAPE} = \frac{\sum \|\text{Error}\|}{\sum \text{Actual}}$ | Avoids division-by-zero during low-wind spells where standard MAPE explodes. |
| **Shortfall Buffer** | P90 of positive signed error ($P_{90}$) | Sizes backup generation covering 9 out of 10 historical wind shortfall occurrences. |
| **No Look-Ahead** | Historical quantiles use strictly prior dates | Prevents predictive leakage when making a decision on day $D-1$. |

Detailed mathematical derivations and references are documented in [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md).

---

## Limitations & Next Steps

1. **One Month Historical Horizon:** This pilot focuses specifically on January 2026. Production systems should train over 12–24 months of seasonal data.
2. **National Aggregation Only:** Data reflects Great Britain national wind generation. Future iterations can break out offshore vs. onshore and regional DNO zones.
3. **No Demand/Price Co-Optimization:** Evaluates wind generation in isolation. Future modules should correlate wind forecast errors with system demand and day-ahead clearing prices.
