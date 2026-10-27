import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatMW } from "../../lib/format";
import type { MetricsResponse } from "../../types";

interface ErrorDistributionChartProps {
  metrics: MetricsResponse;
}

export const ErrorDistributionChart: React.FC<ErrorDistributionChartProps> = ({ metrics }) => {
  const { kpis } = metrics;
  const quantilesData = [
    { label: "P5", value: kpis.signed_p5, desc: "95% of errors were higher than this" },
    { label: "P10", value: kpis.signed_p10, desc: "10th percentile of signed error" },
    { label: "P50 (Median)", value: kpis.signed_p50, desc: "Median error (positive = over-forecast)" },
    { label: "P90 (Buffer)", value: kpis.signed_p90, desc: "90% of over-forecast errors were <= this" },
    { label: "P95", value: kpis.signed_p95, desc: "Extreme over-forecast risk" },
  ].filter((d) => d.value !== null && d.value !== undefined);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="rounded-lg border bg-background p-2.5 shadow-md text-xs space-y-1">
          <p className="font-semibold">{item.label}</p>
          <p className="font-mono font-bold text-foreground">{formatMW(item.value)}</p>
          <p className="text-muted-foreground">{item.desc}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="mb-3">
        <h4 className="text-sm font-semibold">Signed Error Distribution Quantiles</h4>
        <p className="text-xs text-muted-foreground">
          Distribution of (Forecast − Actual) across the selected decision window. Positive values represent over-forecasting (shortfall risk).
        </p>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={quantilesData} margin={{ top: 10, right: 10, left: 0, bottom: 15 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "hsl(var(--border))" }}
            />
            <YAxis
              tick={{ fontSize: 10 }}
              tickFormatter={(v) => `${(v / 1000).toFixed(1)}GW`}
              tickLine={false}
              axisLine={{ stroke: "hsl(var(--border))" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="hsl(var(--foreground))" strokeWidth={1.5} />
            <Bar dataKey="value" radius={[3, 3, 0, 0]}>
              {quantilesData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={(entry.value ?? 0) >= 0 ? "hsl(var(--primary))" : "#059669"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
