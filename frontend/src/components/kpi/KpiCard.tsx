import React from "react";
import { Info } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import { Skeleton } from "../ui/skeleton";

interface KpiCardProps {
  label: string;
  value: string;
  subtext?: string;
  tooltipText: string;
  isLoading?: boolean;
  valueClassName?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  subtext,
  tooltipText,
  isLoading = false,
  valueClassName = "",
}) => {
  return (
    <Card className="shadow-sm">
      <CardContent className="p-4">
        <div className="flex items-center justify-between text-muted-foreground mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider">{label}</span>
          <TooltipProvider delayDuration={150}>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  aria-label={`About ${label}`}
                  className="rounded-full p-0.5 hover:bg-muted text-muted-foreground/70 hover:text-foreground"
                >
                  <Info className="h-3.5 w-3.5" />
                </button>
              </TooltipTrigger>
              <TooltipContent className="max-w-xs text-xs">
                {tooltipText}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>

        {isLoading ? (
          <Skeleton className="h-8 w-24 my-1" />
        ) : (
          <div className={`text-2xl font-bold tracking-tight ${valueClassName}`}>
            {value}
          </div>
        )}

        {subtext && (
          <p className="text-[11px] text-muted-foreground mt-1 truncate">{subtext}</p>
        )}
      </CardContent>
    </Card>
  );
};
