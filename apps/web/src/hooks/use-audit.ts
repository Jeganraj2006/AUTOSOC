import { useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { fetchApi } from "@/lib/api";

export type AuditRecord = {
  id: string;
  timestamp: string;
  actor_id: string;
  actor_name?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  result: string;
  correlation_id?: string;
  metadata?: Record<string, unknown> | unknown[];
};

export type AuditParams = {
  action?: string;
  actor?: string;
  resource_type?: string;
  resource_id?: string;
  start_time?: string;
  end_time?: string;
  sort_direction?: "asc" | "desc";
  limit?: number;
  offset?: number;
};

export type AuditPage = { records: AuditRecord[]; page: { total: number; limit: number; offset: number } };

export function useAuditRecords(params: AuditParams = {}) {
  const { data: session, status } = useSession();
  return useQuery({
    queryKey: ["audit", params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== "") searchParams.append(key, String(value));
      });
      return fetchApi<AuditPage>(`/audit/?${searchParams.toString()}`, {
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      });
    },
    enabled: status === "authenticated" && !!session?.accessToken,
  });
}
