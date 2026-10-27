"""FastAPI application factory, middleware, exception handlers, and routing."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import routes_export, routes_forecast, routes_meta, routes_metrics
from app.core.config import settings
from app.core.errors import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.data.repository import get_repository

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    repo = get_repository()
    if settings.actuals_path.exists() and settings.forecasts_path.exists():
        logger.info("Found processed parquet files at startup, loading...")
        repo.load(settings.actuals_path, settings.forecasts_path)
    else:
        logger.warning(
            "Parquet files not found at %s / %s. Run ingestion pipeline to populate data.",
            settings.actuals_path,
            settings.forecasts_path,
        )
    yield


def create_app() -> FastAPI:
    setup_logging(settings.log_level, json_logs=(settings.environment == "production"))

    app = FastAPI(
        title="UK Wind Forecast Decision Dashboard API",
        description="Day-ahead wind generation forecast evaluation and decision support using Elexon BMRS data.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and timing middleware
    @app.middleware("http")
    async def request_middleware(request: Request, call_next: Any) -> Any:
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response

    # Exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Health check endpoint
    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, Any]:
        repo = get_repository()
        return {
            "status": "ok",
            "data_loaded": repo.is_loaded,
            "actuals_rows": len(repo.actuals) if repo.is_loaded else 0,
            "forecast_rows": len(repo.forecasts) if repo.is_loaded else 0,
        }

    # API v1 routes
    prefix = settings.api_prefix
    app.include_router(routes_meta.router, prefix=prefix, tags=["metadata"])
    app.include_router(routes_forecast.router, prefix=prefix, tags=["forecast"])
    app.include_router(routes_metrics.router, prefix=prefix, tags=["metrics"])
    app.include_router(routes_export.router, prefix=prefix, tags=["export"])

    # Production frontend static serving
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    return app


app = create_app()
