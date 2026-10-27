import React, { useState } from "react";
import { Download, ChevronLeft, ChevronRight, ArrowUpDown } from "lucide-react";
import { Button } from "../ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { formatTimeSlot, formatDateTime } from "../../lib/dates";
import { formatHorizon, formatMW } from "../../lib/format";
import type { Slot } from "../../types";

interface DataTableProps {
  slots: Slot[];
  exportUrl?: string;
}

export const DataTable: React.FC<DataTableProps> = ({ slots, exportUrl }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [sortField, setSortField] = useState<keyof Slot>("start_time");
  const [sortAsc, setSortAsc] = useState(true);
  const pageSize = 12;

  const sortedSlots = [...slots].sort((a, b) => {
    const valA = a[sortField];
    const valB = b[sortField];
    if (valA === valB) return 0;
    if (valA === null || valA === undefined) return 1;
    if (valB === null || valB === undefined) return -1;
    if (valA < valB) return sortAsc ? -1 : 1;
    return sortAsc ? 1 : -1;
  });

  const totalPages = Math.ceil(sortedSlots.length / pageSize) || 1;
  const paginatedSlots = sortedSlots.slice(
    currentPage * pageSize,
    (currentPage + 1) * pageSize
  );

  const handleSort = (field: keyof Slot) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold tracking-tight">
            Half-Hourly Dispatch & Forecast Records
          </h3>
          <p className="text-xs text-muted-foreground">
            Complete slot-level breakdown with publication times and calculated error.
          </p>
        </div>

        {exportUrl && (
          <a href={exportUrl} download="wind_forecast_export.csv">
            <Button variant="outline" size="sm" className="flex items-center gap-1.5">
              <Download className="h-4 w-4" />
              Download CSV
            </Button>
          </a>
        )}
      </div>

      <div className="rounded-lg border bg-card overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/30">
              <TableHead
                className="cursor-pointer select-none"
                onClick={() => handleSort("start_time")}
              >
                <div className="flex items-center gap-1">
                  Time (London)
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer select-none text-right"
                onClick={() => handleSort("forecast_mw")}
              >
                <div className="flex items-center justify-end gap-1">
                  Forecast (MW)
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer select-none text-right"
                onClick={() => handleSort("actual_mw")}
              >
                <div className="flex items-center justify-end gap-1">
                  Actual (MW)
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer select-none text-right"
                onClick={() => handleSort("error_mw")}
              >
                <div className="flex items-center justify-end gap-1">
                  Error (MW)
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </TableHead>
              <TableHead className="text-right">Lead Horizon</TableHead>
              <TableHead>Publish Time (UTC)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedSlots.map((slot) => {
              const err = slot.error_mw;
              return (
                <TableRow key={slot.start_time}>
                  <TableCell className="font-mono text-xs font-medium">
                    {formatTimeSlot(slot.start_time)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs">
                    {slot.has_forecast && slot.forecast_mw !== null ? (
                      formatMW(slot.forecast_mw)
                    ) : (
                      <span className="text-destructive font-medium">Missing</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs">
                    {formatMW(slot.actual_mw)}
                  </TableCell>
                  <TableCell
                    className={`text-right font-mono text-xs font-semibold ${
                      err === null
                        ? ""
                        : err > 0
                          ? "text-destructive"
                          : "text-emerald-600 dark:text-emerald-500"
                    }`}
                  >
                    {err === null ? "—" : err > 0 ? `+${formatMW(err)}` : formatMW(err)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-muted-foreground">
                    {formatHorizon(slot.horizon_h)}
                  </TableCell>
                  <TableCell className="font-mono text-[11px] text-muted-foreground">
                    {slot.publish_time ? formatDateTime(slot.publish_time) : "—"}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Pagination controls */}
      <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
        <span>
          Showing {currentPage * pageSize + 1}–
          {Math.min((currentPage + 1) * pageSize, sortedSlots.length)} of{" "}
          {sortedSlots.length} slots
        </span>
        <div className="flex items-center space-x-1">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
            disabled={currentPage === 0}
            className="h-7 w-7 p-0"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
          </Button>
          <span className="px-2">
            Page {currentPage + 1} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={currentPage >= totalPages - 1}
            className="h-7 w-7 p-0"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
};
