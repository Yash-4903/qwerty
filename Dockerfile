# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Dependencies
FROM python:3.12-slim AS python-builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip uv

COPY backend/pyproject.toml ./backend/
RUN uv pip install --system --no-cache "backend/[dev]" || pip install --no-cache-dir \
    fastapi uvicorn[standard] gunicorn pydantic pydantic-settings pandas pyarrow httpx tenacity python-multipart

# Stage 3: Production Runtime
FROM python:3.12-slim AS runner
WORKDIR /app

# Non-root user
RUN useradd -m -u 1000 appuser

# Copy installed Python site-packages & binaries from builder
COPY --from=python-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Copy backend application code
COPY backend/ ./backend/
# Copy committed processed parquet data
COPY data/processed/ ./data/processed/
# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app/backend \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen(f'http://localhost:{__import__(\"os\").environ.get(\"PORT\", 8000)}/health')" || exit 1

EXPOSE 8000

CMD ["sh", "-c", "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT}"]
