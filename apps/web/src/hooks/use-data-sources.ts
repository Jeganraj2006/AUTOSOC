import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface DataSource {
  id: string;
  name: string;
  source_type: DataSourceType;
  description?: string;
  enabled: boolean;
  environment: string;
  secret_reference?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProvisionedDataSource extends DataSource {
  /** Returned only once by POST /data-sources; never present in list responses. */
  api_key: string;
}

export interface DataSourceCreate {
  name: string;
  source_type: DataSourceType;
  description?: string | null;
  enabled?: boolean;
  environment?: string;
  secret_reference?: string | null;
}

export const dataSourceTypes = [
  "synthetic",
  "http_json",
  "linux_syslog",
  "network_flow",
  "windows_event",
  "kubernetes_audit",
  "aws_cloudtrail",
] as const;

export type DataSourceType = (typeof dataSourceTypes)[number];

export interface DataSourceUpdate {
  name?: string;
  description?: string | null;
  enabled?: boolean;
  environment?: string;
  secret_reference?: string | null;
}

export function useDataSources() {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["data-sources"],
    queryFn: () =>
      fetchApi<{ items: DataSource[]; total: number }>("/data-sources", {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken,
  });
}

export function useCreateDataSource() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newSource: DataSourceCreate) =>
      fetchApi<ProvisionedDataSource>("/data-sources", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newSource),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["data-sources"] });
    },
  });
}

export function useUpdateDataSource() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: DataSourceUpdate }) =>
      fetchApi<DataSource>(`/data-sources/${id}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["data-sources"] });
    },
  });
}
