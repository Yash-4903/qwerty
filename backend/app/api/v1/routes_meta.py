from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_repo
from app.core.config import settings
from app.data.repository import DataRepository
from app.schemas.meta import MetaResponse

router = APIRouter()


@router.get("/meta", response_model=MetaResponse)
def get_meta(repo: DataRepository = Depends(get_repo)) -> MetaResponse:
    coverage_start = ""
    coverage_end = ""
    if repo.is_loaded and not repo.actuals.empty:
        st = repo.actuals["start_time"]
        coverage_start = st.min().isoformat()
        coverage_end = st.max().isoformat()

    return MetaResponse(
        min_decision_date=settings.min_decision_date,
        max_decision_date=settings.max_decision_date,
        default_cutoff=settings.default_cutoff_time,
        timezone=settings.timezone,
        data_coverage_start=coverage_start,
        data_coverage_end=coverage_end,
        assumptions_summary=(
            "Decision date D-1 is in January 2026. Delivery date D is D-1 + 1 day. "
            "Default cutoff 09:00 Europe/London. All internal computations in UTC. "
            "Error = forecast - actual (positive = over-forecast = shortfall risk). "
            "wMAPE = sum(|error|) / sum(actual). "
            "No look-ahead: uncertainty bands derived strictly from prior decision dates."
        ),
        last_data_refresh="Elexon BMRS January 2026",
    )
