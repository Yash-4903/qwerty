from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_repo
from app.core.config import settings
from app.data.repository import DataRepository
from app.domain.cutoff import parse_cutoff_time
from app.schemas.forecast import ForecastResponse
from app.services.forecast_service import get_forecast_for_decision_date

router = APIRouter()

MIN_DATE = date.fromisoformat(settings.min_decision_date)
MAX_DATE = date.fromisoformat(settings.max_decision_date)


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    decision_date: date = Query(
        ..., description="Decision date (D-1), must be within January 2026"
    ),
    cutoff: str = Query(
        default=settings.default_cutoff_time, description="Cutoff time HH:MM (Europe/London)"
    ),
    repo: DataRepository = Depends(get_repo),
) -> ForecastResponse:
    if not (MIN_DATE <= decision_date <= MAX_DATE):
        raise HTTPException(
            status_code=400,
            detail=f"decision_date must be between {MIN_DATE} and {MAX_DATE}",
        )
    try:
        parse_cutoff_time(cutoff)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not repo.is_loaded:
        raise HTTPException(status_code=503, detail="Data repository not loaded")

    return get_forecast_for_decision_date(repo, decision_date, cutoff)
