import React from "react";
import { KpiCard } from "./KpiCard";
import { formatMW, formatPercent } from "../../lib/format";
import type { KpiData } from "../../types";

interface KpiGridProps {
  kpis?: KpiData;
  isLoading?: boolean;
}

export const KpiGrid: React.FC<KpiGridProps> = ({ kpis, isLoading = false }) => {
  const biasVal = kpis?.bias ?? 0;
  const biasColor =
    biasVal > 50
      ? "text-amber-600 dark:text-amber-500"
      : biasVal < -50
        ? "text-emerald-600 dark:text-emerald-500"
        : "text-foreground";

  const totalPossible = (kpis?.n ?? 0) + (kpis?.n_missing_forecast ?? 0);
  const coveragePercent = totalPossible > 0 ? (kpis?.n ?? 0) / totalPossible : null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <KpiCard
        label="MAE"
        value={formatMW(kpis?.mae)}
        subtext="Mean Absolute Error"
        tooltipText="Mean absolute difference between cutoff forecast and actual wind generation across all evaluated half-hours."
        isLoading={isLoading}
      />

      <KpiCard
        label="RMSE"
        value={formatMW(kpis?.rmse)}
        subtext="Root Mean Squared Error"
        tooltipText="Penalizes larger forecast errors more heavily than MAE. Useful for sizing reserve capacities against extreme swings."
        isLoading={isLoading}
      />

      <KpiCard
        label="Forecast Bias"
        value={formatMW(kpis?.bias)}
        subtext={biasVal > 0 ? "+ Over-forecast risk" : "- Under-forecast"}
        tooltipText="Mean signed error (Forecast − Actual). Positive indicates system-level over-forecasting (shortfall risk for buyers); negative indicates under-forecasting."
        valueClassName={biasColor}
        isLoading={isLoading}
      />

      <KpiCard
        label="wMAPE"
        value={formatPercent(kpis?.wmape)}
        subtext="Weighted % Error"
        tooltipText="Weighted Mean Absolute Percentage Error (Σ|error| / Σactual). Avoids division-by-zero during low-wind periods."
        isLoading={isLoading}
      />

      <KpiCard
        label="P90 Abs Error"
        value={formatMW(kpis?.p90_abs_error)}
        subtext="90% of slots error ≤ this"
        tooltipText="90th percentile of absolute error magnitude across all evaluated slots."
        isLoading={isLoading}
      />

      <KpiCard
        label="Data Coverage"
        value={formatPercent(coveragePercent)}
        subtext={`${kpis?.n ?? 0} / ${totalPossible} slots`}
        tooltipText="Percentage of half-hourly delivery slots with a published forecast available prior to the cutoff time."
        isLoading={isLoading}
      />
    </div>
  );
};
