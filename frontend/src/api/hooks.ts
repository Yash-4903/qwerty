import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";

export function useMeta() {
  return useQuery({
    queryKey: ["meta"],
    queryFn: () => apiClient.getMeta(),
    staleTime: 60 * 60 * 1000,
  });
}

export function useForecast(decisionDate: string | null, cutoff: string) {
  return useQuery({
    queryKey: ["forecast", decisionDate, cutoff],
    queryFn: () => apiClient.getForecast(decisionDate!, cutoff),
    enabled: !!decisionDate,
    staleTime: 5 * 60 * 1000,
  });
}

export function useMetrics(start: string, end: string, cutoff: string) {
  return useQuery({
    queryKey: ["metrics", start, end, cutoff],
    queryFn: () => apiClient.getMetrics(start, end, cutoff),
    staleTime: 5 * 60 * 1000,
  });
}
