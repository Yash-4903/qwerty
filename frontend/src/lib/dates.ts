import { format, parseISO } from "date-fns";
import { formatInTimeZone } from "date-fns-tz";

export const LONDON_TZ = "Europe/London";

export function formatDate(d: string | Date): string {
  const dt = typeof d === "string" ? parseISO(d) : d;
  return format(dt, "dd MMM yyyy");
}

export function formatTimeSlot(d: string | Date): string {
  const dt = typeof d === "string" ? parseISO(d) : d;
  return formatInTimeZone(dt, LONDON_TZ, "HH:mm");
}

export function formatDateTime(d: string | Date): string {
  const dt = typeof d === "string" ? parseISO(d) : d;
  return formatInTimeZone(dt, LONDON_TZ, "dd MMM yyyy HH:mm zzz");
}
