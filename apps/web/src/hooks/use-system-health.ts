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
