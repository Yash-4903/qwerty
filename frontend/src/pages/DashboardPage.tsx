import React, { useEffect, useState } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Header } from "../components/layout/Header";
import { AssumptionsPanel } from "../components/layout/AssumptionsPanel";
import { DecisionDatePicker } from "../components/controls/DecisionDatePicker";
import { CutoffSelect } from "../components/controls/CutoffSelect";
import { DecisionSummary } from "../components/decision/DecisionSummary";
import { KpiGrid } from "../components/kpi/KpiGrid";
import { ForecastVsActualChart } from "../components/charts/ForecastVsActualChart";
import { ErrorByHourChart } from "../components/charts/ErrorByHourChart";
import { ErrorByHorizonChart } from "../components/charts/ErrorByHorizonChart";
import { ErrorDistributionChart } from "../components/charts/ErrorDistributionChart";
import { DailyErrorChart } from "../components/charts/DailyErrorChart";
import { DataTable } from "../components/table/DataTable";
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { useForecast, useMetrics } from "../api/hooks";
import { apiClient } from "../api/client";
import { DEFAULT_CUTOFF } from "../lib/constants";
import { formatDate } from "../lib/dates";

export const DashboardPage: React.FC = () => {
  const [assumptionsOpen, setAssumptionsOpen] = useState(false);

  // Sync state with URL query parameters (?date=2026-01-15&cutoff=09:00)
  const [decisionDate, setDecisionDate] = useState<string>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("date") || "2026-01-15";
  });

  const [cutoff, setCutoff] = useState<string>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("cutoff") || DEFAULT_CUTOFF;
  });

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    params.set("date", decisionDate);
    params.set("cutoff", cutoff);
    const newRelativePathQuery = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState(null, "", newRelativePathQuery);
  }, [decisionDate, cutoff]);

  // Queries
  const forecastQuery = useForecast(decisionDate, cutoff);
  const metricsQuery = useMetrics("2026-01-01", "2026-01-31", cutoff);

  const deliveryDateFormatted = forecastQuery.data?.delivery_date
    ? formatDate(forecastQuery.data.delivery_date)
    : undefined;

  const exportUrl = apiClient.getExportUrl(decisionDate, decisionDate, cutoff);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header onOpenAssumptions={() => setAssumptionsOpen(true)} />
      <AssumptionsPanel open={assumptionsOpen} onOpenChange={setAssumptionsOpen} />

      <main className="flex-1 container mx-auto px-4 py-6 space-y-6 max-w-7xl">
        {/* Controls Bar */}
        <Card className="border bg-card/80 backdrop-blur shadow-sm">
          <CardContent className="p-4 sm:p-5">
            <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
                <DecisionDatePicker
                  value={decisionDate}
                  onChange={setDecisionDate}
                  disabled={forecastQuery.isLoading}
                />
                <CutoffSelect
                  value={cutoff}
                  onChange={setCutoff}
                  disabled={forecastQuery.isLoading}
                />
              </div>

              {/* Informative Read-out Banner */}
              <div className="rounded-lg bg-primary/[0.06] border border-primary/20 p-3 flex flex-col justify-center">
                <p className="text-xs font-semibold text-primary">
                  Decision Cutoff Context
                </p>
                <p className="text-xs text-foreground mt-0.5">
                  Decision made on <strong>{formatDate(decisionDate)}</strong> at{" "}
                  <strong>{cutoff} London</strong> &rarr; Target Delivery Day:{" "}
                  <strong className="text-primary">{deliveryDateFormatted ?? "..."}</strong>
                </p>
                <p className="text-[11px] text-muted-foreground mt-0.5">
                  Only WINDFOR forecasts published on or before {cutoff} UTC/GMT are selected.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Forecast Query Error State */}
        {forecastQuery.isError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error Loading Forecast</AlertTitle>
            <AlertDescription className="flex items-center justify-between">
              <span>{forecastQuery.error.message}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => forecastQuery.refetch()}
                className="ml-4"
              >
                <RefreshCw className="h-3.5 w-3.5 mr-1" />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Prominent Decision Support Callout */}
        <DecisionSummary
          decision={forecastQuery.data?.decision}
          deliveryDate={deliveryDateFormatted}
          isLoading={forecastQuery.isLoading}
        />

        {/* High-Level January 2026 Accuracy KPIs */}
        <div>
          <div className="flex items-center justify-between mb-2 px-0.5">
            <h2 className="text-sm font-semibold tracking-tight uppercase text-muted-foreground">
              Month-to-Date Accuracy Benchmarks (January 2026)
            </h2>
          </div>
          <KpiGrid
            kpis={metricsQuery.data?.kpis}
            isLoading={metricsQuery.isLoading}
          />
        </div>

        {/* Main Forecast vs Actual Chart */}
        <Card className="shadow-sm">
          <CardContent className="p-5">
            <ForecastVsActualChart slots={forecastQuery.data?.slots ?? []} />
          </CardContent>
        </Card>

        {/* Accuracy Breakdown Tabs */}
        <Card className="shadow-sm">
          <CardContent className="p-5">
            <Tabs defaultValue="by-hour">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b">
                <div>
                  <h3 className="text-sm font-bold tracking-tight">
                    Model Accuracy Diagnostics
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Historical evaluation breakdowns across intraday hours, lead times, and daily trends.
                  </p>
                </div>
                <TabsList className="grid grid-cols-2 sm:grid-cols-4 w-full sm:w-auto">
                  <TabsTrigger value="by-hour">By Hour</TabsTrigger>
                  <TabsTrigger value="by-horizon">By Horizon</TabsTrigger>
                  <TabsTrigger value="distribution">Distribution</TabsTrigger>
                  <TabsTrigger value="daily">Daily Trend</TabsTrigger>
                </TabsList>
              </div>

              <div className="pt-4">
                <TabsContent value="by-hour" className="mt-0">
                  <ErrorByHourChart data={metricsQuery.data?.by_hour ?? []} />
                </TabsContent>

                <TabsContent value="by-horizon" className="mt-0">
                  <ErrorByHorizonChart data={metricsQuery.data?.by_horizon ?? []} />
                </TabsContent>

                <TabsContent value="distribution" className="mt-0">
                  {metricsQuery.data ? (
                    <ErrorDistributionChart metrics={metricsQuery.data} />
                  ) : null}
                </TabsContent>

                <TabsContent value="daily" className="mt-0">
                  <DailyErrorChart data={metricsQuery.data?.by_day ?? []} />
                </TabsContent>
              </div>
            </Tabs>
          </CardContent>
        </Card>

        {/* Slot-level Data Table */}
        <Card className="shadow-sm">
          <CardContent className="p-5">
            <DataTable
              slots={forecastQuery.data?.slots ?? []}
              exportUrl={exportUrl}
            />
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="border-t bg-card py-6 text-xs text-muted-foreground mt-auto">
        <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
          <p>
            Data source: <strong>Elexon Insights Solution (BMRS)</strong> · National Wind Generation only.
          </p>
          <p>
            Built for UK Day-Ahead Power Buyers · Error = Forecast − Actual (MW)
          </p>
        </div>
      </footer>
    </div>
  );
};
