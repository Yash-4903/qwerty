import { API_BASE } from "../lib/constants";
import type { ForecastResponse, MetaResponse, MetricsResponse } from "../types";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    let msg = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errBody = await res.json();
      if (errBody?.error?.message) {
        msg = errBody.error.message;
      }
    } catch {
      // fallback to statusText
    }
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export const apiClient = {
  getMeta: () => fetchJson<MetaResponse>("/api/v1/meta"),

  getForecast: (decisionDate: string, cutoff: string) =>
    fetchJson<ForecastResponse>(
      `/api/v1/forecast?decision_date=${decisionDate}&cutoff=${encodeURIComponent(cutoff)}`,
    ),

  getMetrics: (start: string, end: string, cutoff: string) =>
    fetchJson<MetricsResponse>(
      `/api/v1/metrics?start=${start}&end=${end}&cutoff=${encodeURIComponent(cutoff)}`,
    ),

  getExportUrl: (start: string, end: string, cutoff: string) =>
    `${API_BASE}/api/v1/export.csv?start=${start}&end=${end}&cutoff=${encodeURIComponent(cutoff)}`,
};
