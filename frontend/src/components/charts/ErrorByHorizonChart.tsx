import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatMW } from "../../lib/format";
import type { HorizonRow } from "../../types";

interface ErrorByHorizonChartProps {
  data: HorizonRow[];
}

export const ErrorByHorizonChart: React.FC<ErrorByHorizonChartProps> = ({ data }) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="rounded-lg border bg-background p-2.5 shadow-md text-xs space-y-1">
          <p className="font-semibold">Horizon: {label}</p>
          <p className="text-primary">MAE: {formatMW(item.mae)}</p>
          <p className="text-muted-foreground">RMSE: {formatMW(item.rmse)}</p>
          <p className={item.bias > 0 ? "text-amber-600" : "text-emerald-600"}>
            Bias: {item.bias > 0 ? `+${formatMW(item.bias)}` : formatMW(item.bias)}
          </p>
          <p className="text-muted-foreground">Total Evaluated Pairs: {item.n.toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="mb-3">
        <h4 className="text-sm font-semibold">Forecast Error by Lead Time (Horizon)</h4>
        <p className="text-xs text-muted-foreground">
          Computed across all published forecasts and actual pairs. Demonstrates how error decreases as delivery approaches.
        </p>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 15 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="bucket"
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
            <Legend verticalAlign="top" align="right" wrapperStyle={{ fontSize: "11px" }} />
            <Bar dataKey="mae" name="MAE (MW)" fill="hsl(var(--primary))" radius={[3, 3, 0, 0]} />
            <Bar dataKey="rmse" name="RMSE (MW)" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
