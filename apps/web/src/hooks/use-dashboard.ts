import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface DashboardSummary {
  total_events_24h: number;
  categories: { category: string; count: number }[];
  timeline: { time: string; count: number }[];
  sources: { source: string; count: number }[];
}

export function useDashboardSummary() {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: () =>
      fetchApi<DashboardSummary>("/events/dashboard/summary", {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken,
    refetchInterval: 1000 * 60, // Refetch every minute
  });
}

export function useSeedDashboardTelemetry() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      fetchApi<{ count: number }>("/events/seed", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard", "summary"] });
    },
  });
}
