import React from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatDate } from "../../lib/dates";
import { formatMW } from "../../lib/format";
import type { DayRow } from "../../types";

interface DailyErrorChartProps {
  data: DayRow[];
}

export const DailyErrorChart: React.FC<DailyErrorChartProps> = ({ data }) => {
  const chartData = data.map((d) => ({
    dateStr: d.date,
    dateLabel: formatDate(d.date),
    mae: d.mae,
    rmse: d.rmse,
    bias: d.bias,
    n: d.n,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="rounded-lg border bg-background p-2.5 shadow-md text-xs space-y-1">
          <p className="font-semibold">{item.dateLabel}</p>
          <p className="text-primary">MAE: {formatMW(item.mae)}</p>
          <p className="text-purple-600">RMSE: {formatMW(item.rmse)}</p>
          <p className={item.bias > 0 ? "text-amber-600" : "text-emerald-600"}>
            Bias: {item.bias > 0 ? `+${formatMW(item.bias)}` : formatMW(item.bias)}
          </p>
          <p className="text-muted-foreground">Slots: {item.n}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="mb-3">
        <h4 className="text-sm font-semibold">Daily Error Trend</h4>
        <p className="text-xs text-muted-foreground">
          MAE, RMSE, and Bias progression over the January 2026 decision window.
        </p>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 15 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="dateLabel"
              tick={{ fontSize: 10 }}
              interval={4}
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
            <ReferenceLine y={0} stroke="hsl(var(--border))" />
            <Line
              type="monotone"
              dataKey="mae"
              name="MAE (MW)"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={{ r: 2 }}
            />
            <Line
              type="monotone"
              dataKey="rmse"
              name="RMSE (MW)"
              stroke="#8b5cf6"
              strokeWidth={1.5}
              dot={{ r: 2 }}
            />
            <Line
              type="monotone"
              dataKey="bias"
              name="Bias (MW)"
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={{ r: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
