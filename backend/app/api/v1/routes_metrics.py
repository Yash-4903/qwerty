from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_repo
from app.core.config import settings
from app.data.repository import DataRepository
from app.domain.cutoff import parse_cutoff_time
from app.schemas.metrics import MetricsResponse
from app.services.metrics_service import get_metrics_for_range

router = APIRouter()

MIN_DATE = date.fromisoformat(settings.min_decision_date)
MAX_DATE = date.fromisoformat(settings.max_decision_date)


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    start: date = Query(default=MIN_DATE, description="Start decision date"),
    end: date = Query(default=MAX_DATE, description="End decision date"),
    cutoff: str = Query(default=settings.default_cutoff_time, description="Cutoff time HH:MM"),
    repo: DataRepository = Depends(get_repo),
) -> MetricsResponse:
    if not (MIN_DATE <= start <= MAX_DATE):
        raise HTTPException(
            status_code=400, detail=f"start must be between {MIN_DATE} and {MAX_DATE}"
        )
    if not (MIN_DATE <= end <= MAX_DATE):
        raise HTTPException(
            status_code=400, detail=f"end must be between {MIN_DATE} and {MAX_DATE}"
        )
    if start > end:
        raise HTTPException(status_code=400, detail="start date must be on or before end date")
    try:
        parse_cutoff_time(cutoff)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not repo.is_loaded:
        raise HTTPException(status_code=503, detail="Data repository not loaded")

    return get_metrics_for_range(repo, start, end, cutoff)
