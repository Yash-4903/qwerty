export function formatMW(value: number | null | undefined, decimals = 0): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "—";
  }
  return `${value.toLocaleString("en-GB", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })} MW`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "—";
  }
  return `${(value * 100).toFixed(1)}%`;
}

export function formatHorizon(hours: number | null | undefined): string {
  if (hours === null || hours === undefined || isNaN(hours)) {
    return "—";
  }
  return `${hours.toFixed(1)}h`;
}
