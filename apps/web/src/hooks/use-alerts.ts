import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface AlertResponse {
  id: string;
  title: string;
  description?: string;
  severity: string;
  status: string;
  source_event_id?: string;
  rule_id?: string;
  indicators_json?: Record<string, unknown> | unknown[];
  incident_id?: string;
  created_at: string;
  updated_at: string;
}

export interface UseAlertsParams {
  q?: string;
  status?: string;
  severity?: string;
  incident_id?: string;
  rule_id?: string;
  start_time?: string;
  end_time?: string;
  sort_field?: "created_at" | "updated_at" | "severity" | "status" | "title";
  sort_direction?: "asc" | "desc";
  limit?: number;
  offset?: number;
}

export interface AlertPage {
  alerts: AlertResponse[];
  page: { total: number; limit: number; offset: number };
}

export function useAlerts(params: UseAlertsParams = {}) {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["alerts", params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params.status) searchParams.append("status", params.status);
      if (params.severity) searchParams.append("severity", params.severity);
      if (params.limit !== undefined) searchParams.append("limit", params.limit.toString());
      if (params.offset !== undefined) searchParams.append("offset", params.offset.toString());

      return fetchApi<AlertResponse[]>(`/alerts/?${searchParams.toString()}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      });
    },
    enabled: authStatus === "authenticated" && !!session?.accessToken,
  });
}

export function useAlertSearch(params: UseAlertsParams = {}) {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["alerts", "search", params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== "") searchParams.append(key, String(value));
      });
      return fetchApi<AlertPage>(`/alerts/search?${searchParams.toString()}`, {
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      });
    },
    enabled: authStatus === "authenticated" && !!session?.accessToken,
  });
}

export function useAlert(alertId: string) {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["alerts", alertId],
    queryFn: () =>
      fetchApi<AlertResponse>(`/alerts/${alertId}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: authStatus === "authenticated" && !!session?.accessToken && !!alertId,
  });
}

export function useUpdateAlertStatus() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ alertId, status }: { alertId: string; status: string }) =>
      fetchApi<AlertResponse>(`/alerts/${alertId}/status`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
        body: JSON.stringify({ status }),
      }),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      queryClient.setQueryData(["alerts", variables.alertId], data);
    },
  });
}
