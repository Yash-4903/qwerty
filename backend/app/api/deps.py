from __future__ import annotations

from app.data.repository import DataRepository, get_repository


def get_repo() -> DataRepository:
    return get_repository()
