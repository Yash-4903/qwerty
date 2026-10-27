import React from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatTimeSlot, formatDateTime } from "../../lib/dates";
import { formatHorizon, formatMW } from "../../lib/format";
import type { Slot } from "../../types";

interface ForecastVsActualChartProps {
  slots: Slot[];
}

export const ForecastVsActualChart: React.FC<ForecastVsActualChartProps> = ({ slots }) => {
  const chartData = slots.map((s) => ({
    timeLabel: formatTimeSlot(s.start_time),
    startTime: s.start_time,
    forecast: s.forecast_mw,
    actual: s.actual_mw,
    bandLow: s.band_low,
    bandHigh: s.band_high,
    // For shaded uncertainty band between low and high:
    bandRange:
      s.band_low !== null && s.band_high !== null
        ? [s.band_low, s.band_high]
        : null,
    publishTime: s.publish_time,
    horizonHours: s.horizon_h,
    error: s.error_mw,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="rounded-lg border bg-background p-3 shadow-md text-xs space-y-1.5">
          <p className="font-semibold text-foreground border-b pb-1">
            Slot: {formatDateTime(data.startTime)}
          </p>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1">
            <span className="text-muted-foreground">Forecast (at cutoff):</span>
            <span className="font-mono font-medium text-right text-primary">
              {formatMW(data.forecast)}
            </span>

            <span className="text-muted-foreground">Actual Generation:</span>
            <span className="font-mono font-medium text-right text-emerald-600 dark:text-emerald-500">
              {formatMW(data.actual)}
            </span>

            {data.error !== null && (
              <>
                <span className="text-muted-foreground">Forecast Error:</span>
                <span
                  className={`font-mono font-medium text-right ${
                    data.error > 0 ? "text-destructive" : "text-emerald-600"
                  }`}
                >
                  {data.error > 0 ? `+${formatMW(data.error)}` : formatMW(data.error)}
                </span>
              </>
            )}

            {data.bandLow !== null && data.bandHigh !== null && (
              <>
                <span className="text-muted-foreground">90% Confidence Band:</span>
                <span className="font-mono text-right text-muted-foreground">
                  {formatMW(data.bandLow)} – {formatMW(data.bandHigh)}
                </span>
              </>
            )}

            {data.publishTime && (
              <>
                <span className="text-muted-foreground">Published At:</span>
                <span className="font-mono text-right text-muted-foreground">
                  {formatDateTime(data.publishTime)}
                </span>
              </>
            )}

            {data.horizonHours !== null && (
              <>
                <span className="text-muted-foreground">Lead Horizon:</span>
                <span className="font-mono text-right text-muted-foreground">
                  {formatHorizon(data.horizonHours)}
                </span>
              </>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold tracking-tight">
            Delivery Day Generation: Forecast vs Actual
          </h3>
          <p className="text-xs text-muted-foreground">
            Half-hourly wind generation with empirical uncertainty band derived from historical error quantiles.
          </p>
        </div>
      </div>

      <div className="h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{ top: 10, right: 10, left: 0, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="timeLabel"
              tick={{ fontSize: 11 }}
              interval={3}
              tickLine={false}
              axisLine={{ stroke: "hsl(var(--border))" }}
              label={{
                value: "Time (Europe/London)",
                position: "insideBottom",
                offset: -12,
                fontSize: 11,
                fill: "hsl(var(--muted-foreground))",
              }}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => `${(v / 1000).toFixed(0)} GW`}
              tickLine={false}
              axisLine={{ stroke: "hsl(var(--border))" }}
              label={{
                value: "Generation (MW)",
                angle: -90,
                position: "insideLeft",
                offset: 15,
                fontSize: 11,
                fill: "hsl(var(--muted-foreground))",
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ paddingBottom: "10px", fontSize: "12px" }}
            />

            {/* Shaded Area for Uncertainty Band */}
            <Area
              type="monotone"
              dataKey="bandRange"
              name="Uncertainty Band (Empirical P10–P90)"
              fill="hsl(var(--primary))"
              fillOpacity={0.12}
              stroke="none"
              legendType="circle"
            />

            {/* Forecast Line */}
            <Line
              type="monotone"
              dataKey="forecast"
              name="Forecast (at Cutoff)"
              stroke="hsl(var(--primary))"
              strokeWidth={2.5}
              dot={{ r: 2, fill: "hsl(var(--primary))" }}
              activeDot={{ r: 5 }}
            />

            {/* Actuals Line */}
            <Line
              type="monotone"
              dataKey="actual"
              name="Actual Generation"
              stroke="#059669"
              strokeWidth={2}
              strokeDasharray="4 3"
              dot={{ r: 2, fill: "#059669" }}
              activeDot={{ r: 5 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
