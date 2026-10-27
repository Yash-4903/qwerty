import React from "react";
import { Calendar } from "lucide-react";
import { formatDate } from "../../lib/dates";

interface DecisionDatePickerProps {
  value: string;
  onChange: (dateStr: string) => void;
  disabled?: boolean;
}

export const DecisionDatePicker: React.FC<DecisionDatePickerProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="flex flex-col space-y-1.5">
      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
        <Calendar className="h-3.5 w-3.5 text-primary" />
        Decision Date (D-1)
      </label>
      <div className="relative">
        <input
          type="date"
          min="2026-01-01"
          max="2026-01-31"
          value={value}
          onChange={(e) => {
            if (e.target.value) {
              onChange(e.target.value);
            }
          }}
          disabled={disabled}
          className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>
      <span className="text-[11px] text-muted-foreground">
        Selected: {formatDate(value)} (January 2026 only)
      </span>
    </div>
  );
};
