import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface SystemHealth {
  status: string;
  version?: string;
  environment?: string;
  components?: Record<string, string>;
  dependencies?: {
    database?: string;
    redis?: string;
    opensearch?: string;
    redpanda?: string;
  };
}

export interface OperationalComponent {
  name: string;
  status: "healthy" | "degraded" | "unavailable" | "unknown";
  detail?: string;
  last_successful_operation?: string;
  last_heartbeat?: string;
  failed_processing_count?: number;
  retry_or_dlq_count?: number;
  model_identifier?: string;
}

export interface OperationalHealth { components: OperationalComponent[]; checked_at: string; limitations: string[] }

export function useSystemHealth() {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["system-health"],
    queryFn: () =>
      fetchApi<SystemHealth>("/health/live", {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: authStatus === "authenticated" && !!session?.accessToken,
    refetchInterval: 1000 * 30, // Every 30 seconds
  });
}

export function useOperationalHealth() {
  const { data: session, status: authStatus } = useSession();
  return useQuery({
    queryKey: ["system-health", "operations"],
    queryFn: () => fetchApi<OperationalHealth>("/health/operations", {
      headers: { Authorization: `Bearer ${session?.accessToken}` },
    }),
    enabled: authStatus === "authenticated" && !!session?.accessToken,
    refetchInterval: 1000 * 60,
  });
}
