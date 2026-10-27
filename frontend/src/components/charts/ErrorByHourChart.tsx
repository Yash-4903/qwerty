import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatMW } from "../../lib/format";
import type { HourRow } from "../../types";

interface ErrorByHourChartProps {
  data: HourRow[];
}

export const ErrorByHourChart: React.FC<ErrorByHourChartProps> = ({ data }) => {
  const chartData = data.map((d) => ({
    hourLabel: `${String(d.hour).padStart(2, "0")}:00`,
    mae: d.mae,
    bias: d.bias,
    n: d.n,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="rounded-lg border bg-background p-2.5 shadow-md text-xs space-y-1">
          <p className="font-semibold">{label} UTC</p>
          <p className="text-primary">MAE: {formatMW(item.mae)}</p>
          <p className={item.bias > 0 ? "text-amber-600" : "text-emerald-600"}>
            Bias: {item.bias > 0 ? `+${formatMW(item.bias)}` : formatMW(item.bias)}
          </p>
          <p className="text-muted-foreground">Sample Size: {item.n} slots</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="mb-3">
        <h4 className="text-sm font-semibold">Forecast Error by Hour of Day</h4>
        <p className="text-xs text-muted-foreground">
          Average error magnitude (MAE) and directional tendency (Bias) for each hour (UTC).
        </p>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 15 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="hourLabel"
              tick={{ fontSize: 10 }}
              interval={2}
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
            <Bar dataKey="mae" name="Mean Absolute Error (MAE)" fill="hsl(var(--primary))" radius={[3, 3, 0, 0]} />
            <Bar dataKey="bias" name="Forecast Bias" fill="#f59e0b" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
