export interface Slot {
  start_time: string;
  forecast_mw: number | null;
  actual_mw: number | null;
  error_mw: number | null;
  publish_time: string | null;
  horizon_h: number | null;
  band_low: number | null;
  band_high: number | null;
  has_forecast: boolean;
}

export interface Decision {
  avg_forecast_mw: number | null;
  peak_forecast_mw: number | null;
  trough_forecast_mw: number | null;
  shortfall_buffer_mw: number | null;
  summary: string;
  n_history_slots: number;
  band_source: string;
}

export interface ForecastResponse {
  decision_date: string;
  delivery_date: string;
  cutoff_utc: string;
  cutoff_london: string;
  slots: Slot[];
  n_missing_forecast: number;
  n_missing_actual: number;
  total_slots: number;
  decision: Decision;
}

export interface KpiData {
  mae: number | null;
  rmse: number | null;
  bias: number | null;
  wmape: number | null;
  n: number;
  p50_abs_error: number | null;
  p90_abs_error: number | null;
  p95_abs_error: number | null;
  signed_p5: number | null;
  signed_p10: number | null;
  signed_p50: number | null;
  signed_p90: number | null;
  signed_p95: number | null;
  n_missing_forecast: number;
  n_missing_actual: number;
}

export interface HorizonRow {
  bucket: string;
  n: number;
  mae: number | null;
  rmse: number | null;
  bias: number | null;
}

export interface HourRow {
  hour: number;
  n: number;
  mae: number | null;
  bias: number | null;
}

export interface DayRow {
  date: string;
  n: number;
  mae: number | null;
  rmse: number | null;
  bias: number | null;
}

export interface MetricsResponse {
  start_date: string;
  end_date: string;
  cutoff: string;
  kpis: KpiData;
  by_hour: HourRow[];
  by_horizon: HorizonRow[];
  by_day: DayRow[];
}

export interface MetaResponse {
  min_decision_date: string;
  max_decision_date: string;
  default_cutoff: string;
  timezone: string;
  data_coverage_start: string;
  data_coverage_end: string;
  assumptions_summary: string;
  last_data_refresh: string;
}
