import React from "react";
import { ShieldAlert, TrendingUp, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { Skeleton } from "../ui/skeleton";
import { formatMW } from "../../lib/format";
import type { Decision } from "../../types";

interface DecisionSummaryProps {
  decision?: Decision;
  deliveryDate?: string;
  isLoading?: boolean;
}

export const DecisionSummary: React.FC<DecisionSummaryProps> = ({
  decision,
  deliveryDate,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <Card className="border-primary/20 bg-primary/[0.02]">
        <CardContent className="p-6">
          <Skeleton className="h-6 w-48 mb-4" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
          <Skeleton className="h-12 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!decision) {
    return null;
  }

  const isFallback = decision.band_source === "full_month_fallback";

  return (
    <Card className="border-primary/30 bg-gradient-to-r from-primary/[0.04] via-background to-primary/[0.02] shadow-sm">
      <CardContent className="p-6">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h2 className="text-base font-bold tracking-tight">
              Day-Ahead Procurement Guidance {deliveryDate ? `(Delivery: ${deliveryDate})` : ""}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {isFallback && (
              <Badge variant="outline" className="border-amber-500/50 text-amber-600 bg-amber-500/10 flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" />
                Full-Month Fallback
              </Badge>
            )}
            <Badge variant="secondary" className="font-mono text-xs">
              n = {decision.n_history_slots.toLocaleString()} historical slots
            </Badge>
          </div>
        </div>

        {/* 4 Primary Procurement Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
          <div className="rounded-lg border bg-card/60 p-3.5">
            <p className="text-xs font-medium text-muted-foreground">Expected Average</p>
            <p className="text-2xl font-bold tracking-tight mt-0.5 text-foreground">
              {formatMW(decision.avg_forecast_mw)}
            </p>
            <p className="text-[11px] text-muted-foreground mt-0.5">Mean Day-Ahead Forecast</p>
          </div>

          <div className="rounded-lg border bg-card/60 p-3.5">
            <p className="text-xs font-medium text-muted-foreground">Generation Peak</p>
            <p className="text-2xl font-bold tracking-tight mt-0.5 text-foreground">
              {formatMW(decision.peak_forecast_mw)}
            </p>
            <p className="text-[11px] text-muted-foreground mt-0.5">Maximum Half-Hour</p>
          </div>

          <div className="rounded-lg border bg-card/60 p-3.5">
            <p className="text-xs font-medium text-muted-foreground">Generation Trough</p>
            <p className="text-2xl font-bold tracking-tight mt-0.5 text-foreground">
              {formatMW(decision.trough_forecast_mw)}
            </p>
            <p className="text-[11px] text-muted-foreground mt-0.5">Minimum Half-Hour</p>
          </div>

          <div className="rounded-lg border border-primary/40 bg-primary/10 p-3.5">
            <p className="text-xs font-semibold text-primary flex items-center gap-1">
              <ShieldAlert className="h-3.5 w-3.5" />
              Suggested Shortfall Buffer
            </p>
            <p className="text-2xl font-extrabold tracking-tight mt-0.5 text-primary">
              {formatMW(decision.shortfall_buffer_mw)}
            </p>
            <p className="text-[11px] text-primary/80 mt-0.5">90% Confidence Over-Forecast Risk</p>
          </div>
        </div>

        {/* Decision Summary Text */}
        <div className="rounded-md bg-muted/60 p-3.5 border border-muted text-sm leading-relaxed text-foreground/90">
          <p className="font-medium text-foreground mb-1 flex items-center gap-1.5">
            <span>Trading Desk Action Plan</span>
          </p>
          <p className="text-sm">{decision.summary}</p>
        </div>
      </CardContent>
    </Card>
  );
};
