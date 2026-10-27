from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MetaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    min_decision_date: str
    max_decision_date: str
    default_cutoff: str
    timezone: str
    data_coverage_start: str
    data_coverage_end: str
    assumptions_summary: str
    last_data_refresh: str
