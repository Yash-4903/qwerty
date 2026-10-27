"""CLI script to ingest data from Elexon BMRS API and produce normalized parquet files.

Usage:
    python -m app.ingestion.fetch_data --start 2025-12-24 --end 2026-02-02
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import settings
from app.ingestion.elexon_client import ElexonClient
from app.ingestion.validate import validate_and_report

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent.parent.parent / "data" / "processed"
DOCS_DIR = Path(__file__).parent.parent.parent.parent / "docs"


def normalise_actuals(raw_rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize raw FUELHH records."""
    if not raw_rows:
        return pd.DataFrame(columns=["start_time", "generation_mw"])

    df = pd.DataFrame(raw_rows)
    # Rename fields
    rename_map = {"startTime": "start_time", "generation": "generation_mw"}
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["generation_mw"] = pd.to_numeric(df["generation_mw"], errors="coerce")

    # Drop nulls and negatives
    df = df.dropna(subset=["start_time", "generation_mw"])
    df = df[df["generation_mw"] >= 0]

    # Deduplicate: if multiple records for same start_time, keep last
    df = df.drop_duplicates(subset=["start_time"], keep="last")
    return df[["start_time", "generation_mw"]].sort_values("start_time").reset_index(drop=True)


def normalise_forecasts(raw_rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize raw WINDFOR records."""
    if not raw_rows:
        return pd.DataFrame(columns=["start_time", "publish_time", "forecast_mw"])

    df = pd.DataFrame(raw_rows)
    rename_map = {
        "startTime": "start_time",
        "publishTime": "publish_time",
        "generation": "forecast_mw",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
    df["forecast_mw"] = pd.to_numeric(df["forecast_mw"], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["start_time", "publish_time", "forecast_mw"])
    df = df[df["forecast_mw"] >= 0]

    # On key conflict (same start_time and publish_time), keep last
    df = df.drop_duplicates(subset=["start_time", "publish_time"], keep="last")
    return (
        df[["start_time", "publish_time", "forecast_mw"]]
        .sort_values(["start_time", "publish_time"])
        .reset_index(drop=True)
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    parser = argparse.ArgumentParser(description="Fetch Elexon BMRS Wind Data")
    parser.add_argument(
        "--start", default="2025-12-24", help="WINDFOR publish start date (YYYY-MM-DD)"
    )
    parser.add_argument("--end", default="2026-02-02", help="Fetch end date (YYYY-MM-DD)")
    args = parser.parse_args()

    start_pub_dt = datetime.fromisoformat(f"{args.start}T00:00:00").replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(f"{args.end}T00:00:00").replace(tzinfo=timezone.utc)

    # Actuals window: delivery days 2026-01-02 to 2026-02-02
    actuals_start_dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    actuals_end_dt = datetime(2026, 2, 2, 0, 0, 0, tzinfo=timezone.utc)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    client = ElexonClient(
        base_url=settings.elexon_base_url,
        api_key=settings.elexon_api_key,
    )

    try:
        # 1. Fetch FUELHH Actuals
        logger.info(
            "Fetching FUELHH Actuals (WIND) from %s to %s", actuals_start_dt, actuals_end_dt
        )
        raw_actuals = client.fetch_fuelhh_wind_stream(actuals_start_dt, actuals_end_dt)
        raw_act_path = RAW_DIR / "fuelhh_wind.json"
        with raw_act_path.open("w", encoding="utf-8") as f:
            json.dump(raw_actuals, f)
        logger.info("Saved %d raw actuals to %s", len(raw_actuals), raw_act_path)

        actuals_df = normalise_actuals(raw_actuals)
        actuals_parquet_path = PROCESSED_DIR / "actuals.parquet"
        actuals_df.to_parquet(actuals_parquet_path, index=False)
        logger.info("Wrote %d normalized actuals to %s", len(actuals_df), actuals_parquet_path)

        # 2. Fetch WINDFOR Forecasts
        logger.info("Fetching WINDFOR Forecasts published from %s to %s", start_pub_dt, end_dt)
        raw_forecasts = client.fetch_windfor_stream(start_pub_dt, end_dt)
        raw_fc_path = RAW_DIR / "windfor.json"
        with raw_fc_path.open("w", encoding="utf-8") as f:
            json.dump(raw_forecasts, f)
        logger.info("Saved %d raw forecasts to %s", len(raw_forecasts), raw_fc_path)

        forecasts_df = normalise_forecasts(raw_forecasts)
        forecasts_parquet_path = PROCESSED_DIR / "forecasts.parquet"
        forecasts_df.to_parquet(forecasts_parquet_path, index=False)
        logger.info(
            "Wrote %d normalized forecasts to %s", len(forecasts_df), forecasts_parquet_path
        )

        # 3. Validate & Generate DATA_NOTES.md
        data_report = validate_and_report(actuals_df, forecasts_df)
        data_notes_path = DOCS_DIR / "DATA_NOTES.md"
        data_notes_path.write_text(data_report, encoding="utf-8")
        logger.info("Generated data notes report at %s", data_notes_path)
        print("\n=== Data Quality Summary ===\n" + data_report)

    finally:
        client.close()


if __name__ == "__main__":
    main()
