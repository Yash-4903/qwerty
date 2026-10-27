.PHONY: dev run test lint typecheck build ingest format clean

dev:
	docker compose up --build

run:
	docker compose -f docker-compose.prod.yml up --build

test:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	cd backend && ruff check app/ tests/
	cd backend && ruff format --check app/ tests/
	cd frontend && npm run build

typecheck:
	cd backend && mypy app/
	cd frontend && npm run typecheck

format:
	cd backend && ruff format app/ tests/
	cd backend && ruff check --fix app/ tests/

ingest:
	cd backend && python -m app.ingestion.fetch_data --start 2025-12-24 --end 2026-02-02

build:
	docker build -t wind-forecast-dashboard .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
