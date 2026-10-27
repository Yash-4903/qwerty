"""HTTP client for Elexon BMRS API with chunking and retries."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any

import certifi
import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
CHUNK_HOURS = 48  # 2 days per chunk for reliable stream response sizes


class ElexonClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, api_key: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Accept": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key

        self._client = httpx.Client(
            headers=headers,
            timeout=60.0,
            verify=certifi.where(),
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ElexonClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @retry(
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1.0, min=2.0, max=30.0),
        reraise=True,
    )
    def _fetch_stream(self, dataset: str, params: dict[str, str]) -> list[dict[str, Any]]:
        url = f"{self.base_url}/datasets/{dataset}/stream"
        logger.debug("GET %s %s", url, params)
        resp = self._client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return list(data)
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            return list(data["data"])
        return []

    def fetch_fuelhh_wind_stream(
        self, start_dt: datetime, end_dt: datetime
    ) -> list[dict[str, Any]]:
        """Fetch FUELHH actual generation in chunks, filtering for WIND."""
        all_rows: list[dict[str, Any]] = []
        curr = start_dt

        while curr < end_dt:
            next_chunk = min(curr + timedelta(hours=CHUNK_HOURS), end_dt)
            logger.info(
                "Fetching FUELHH stream: %s to %s", curr.isoformat(), next_chunk.isoformat()
            )

            params = {
                "publishDateTimeFrom": curr.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "publishDateTimeTo": next_chunk.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            batch = self._fetch_stream("FUELHH", params)
            wind_batch = [item for item in batch if item.get("fuelType") == "WIND"]
            all_rows.extend(wind_batch)

            curr = next_chunk
            time.sleep(0.3)  # Polite rate limiting

        return all_rows

    def fetch_windfor_stream(
        self, publish_start: datetime, publish_end: datetime
    ) -> list[dict[str, Any]]:
        """Fetch WINDFOR forecast generation in chunks by publishDateTime."""
        all_rows: list[dict[str, Any]] = []
        curr = publish_start

        while curr < publish_end:
            next_chunk = min(curr + timedelta(hours=CHUNK_HOURS), publish_end)
            logger.info(
                "Fetching WINDFOR stream: %s to %s", curr.isoformat(), next_chunk.isoformat()
            )

            params = {
                "publishDateTimeFrom": curr.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "publishDateTimeTo": next_chunk.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            batch = self._fetch_stream("WINDFOR", params)
            all_rows.extend(batch)

            curr = next_chunk
            time.sleep(0.3)  # Polite rate limiting

        return all_rows
