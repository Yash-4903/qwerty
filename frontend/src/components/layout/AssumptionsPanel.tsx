import React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";

interface AssumptionsPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const AssumptionsPanel: React.FC<AssumptionsPanelProps> = ({ open, onOpenChange }) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl">Assumptions & Trading Methodology</DialogTitle>
          <DialogDescription>
            Core conventions, domain logic, and scope definitions used across this dashboard.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 text-sm mt-2">
          <div className="rounded-lg border bg-muted/40 p-3">
            <h4 className="font-semibold text-foreground mb-1">1. Decision Cutoff Rule</h4>
            <p className="text-muted-foreground">
              For any delivery day <strong>D</strong>, the procurement decision is made on <strong>D-1</strong> at a configured cutoff time (default: <strong>09:00 Europe/London</strong>).
              GB Day-Ahead power auctions (N2EX / EPEX Spot) close mid-morning (~11:00 London time). A 09:00 cutoff gives the trading team time to analyze forecasts before gate closure.
            </p>
          </div>

          <div className="rounded-lg border bg-muted/40 p-3">
            <h4 className="font-semibold text-foreground mb-1">2. Error Sign Convention</h4>
            <p className="text-muted-foreground">
              <strong>Error = Forecast − Actual (MW)</strong><br />
              • <strong>Positive error:</strong> Over-forecast. Actual wind generation came in lower than predicted. This creates a <em>shortfall risk</em> where the utility must buy expensive prompt/balancing power.<br />
              • <strong>Negative error:</strong> Under-forecast. Actual wind came in higher than predicted.
            </p>
          </div>

          <div className="rounded-lg border bg-muted/40 p-3">
            <h4 className="font-semibold text-foreground mb-1">3. Percentage Error Metric (wMAPE)</h4>
            <p className="text-muted-foreground">
              Standard MAPE divides by individual slot actuals, which explodes during low-wind calm periods. We report <strong>wMAPE = &Sigma;|Error| / &Sigma;Actual</strong>, providing a stable, weighted percentage error for portfolio hedging.
            </p>
          </div>

          <div className="rounded-lg border bg-muted/40 p-3">
            <h4 className="font-semibold text-foreground mb-1">4. Shortfall Buffer & Uncertainty Bands</h4>
            <p className="text-muted-foreground">
              The suggested shortfall buffer is the <strong>P90 quantile of positive signed error</strong>: how much actual wind generation fell below forecast 9 times out of 10.<br />
              <strong>No Look-Ahead Leakage:</strong> Error quantiles for any given date are computed strictly from prior decision days. If fewer than 3 prior days are available, full-month fallback is used and flagged.
            </p>
          </div>

          <div className="rounded-lg border bg-muted/40 p-3">
            <h4 className="font-semibold text-foreground mb-1">5. AI Tools Disclosure</h4>
            <p className="text-muted-foreground">
              In compliance with project requirements: This application was engineered with the assistance of AI coding tools. Scaffolding, architecture, and verification were directed and validated against production engineering standards.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
