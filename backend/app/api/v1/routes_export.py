from __future__ import annotations

import csv
import io
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.api.deps import get_repo
from app.core.config import settings
from app.data.repository import DataRepository
from app.domain.cutoff import parse_cutoff_time
from app.services.forecast_service import get_forecast_for_decision_date

router = APIRouter()

MIN_DATE = date.fromisoformat(settings.min_decision_date)
MAX_DATE = date.fromisoformat(settings.max_decision_date)


@router.get("/export.csv")
def export_csv(
    start: date = Query(default=MIN_DATE),
    end: date = Query(default=MAX_DATE),
    cutoff: str = Query(default=settings.default_cutoff_time),
    repo: DataRepository = Depends(get_repo),
) -> StreamingResponse:
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

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "decision_date",
            "delivery_date",
            "start_time_utc",
            "forecast_mw",
            "actual_mw",
            "error_mw",
            "publish_time_utc",
            "horizon_hours",
            "has_forecast",
            "band_low_mw",
            "band_high_mw",
        ]
    )

    curr = start
    while curr <= end:
        resp = get_forecast_for_decision_date(repo, curr, cutoff)
        for slot in resp.slots:
            writer.writerow(
                [
                    resp.decision_date.isoformat(),
                    resp.delivery_date.isoformat(),
                    slot.start_time.isoformat(),
                    slot.forecast_mw if slot.forecast_mw is not None else "",
                    slot.actual_mw if slot.actual_mw is not None else "",
                    slot.error_mw if slot.error_mw is not None else "",
                    slot.publish_time.isoformat() if slot.publish_time is not None else "",
                    slot.horizon_h if slot.horizon_h is not None else "",
                    slot.has_forecast,
                    slot.band_low if slot.band_low is not None else "",
                    slot.band_high if slot.band_high is not None else "",
                ]
            )
        curr += timedelta(days=1)

    output.seek(0)
    filename = f"wind_forecast_export_{start}_to_{end}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
