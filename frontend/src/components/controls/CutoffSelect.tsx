import React from "react";
import { Clock } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";

interface CutoffSelectProps {
  value: string;
  onChange: (timeStr: string) => void;
  disabled?: boolean;
}

const COMMON_CUTOFFS = [
  { value: "06:00", label: "06:00 (Early Morning)" },
  { value: "07:00", label: "07:00" },
  { value: "08:00", label: "08:00" },
  { value: "09:00", label: "09:00 (Default - Pre-Auction)" },
  { value: "10:00", label: "10:00" },
  { value: "11:00", label: "11:00 (Gate Closure)" },
  { value: "12:00", label: "12:00 (Post-Auction)" },
];

export const CutoffSelect: React.FC<CutoffSelectProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="flex flex-col space-y-1.5">
      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
        <Clock className="h-3.5 w-3.5 text-primary" />
        Decision Cutoff Time
      </label>
      <Select value={value} onValueChange={onChange} disabled={disabled}>
        <SelectTrigger className="h-10 w-full sm:w-[220px]">
          <SelectValue placeholder="Select cutoff" />
        </SelectTrigger>
        <SelectContent>
          {COMMON_CUTOFFS.map((c) => (
            <SelectItem key={c.value} value={c.value}>
              {c.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <span className="text-[11px] text-muted-foreground">
        Europe/London time on D-1
      </span>
    </div>
  );
};
