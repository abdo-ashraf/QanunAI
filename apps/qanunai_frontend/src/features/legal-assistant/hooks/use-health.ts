import { useQuery } from "@tanstack/react-query";
import { fetchHealth, healthKeys } from "../api/health";

/** Polls the backend health endpoint to drive the connection indicator. */
export function useHealth() {
  return useQuery({
    queryKey: healthKeys.all,
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: false,
  });
}
