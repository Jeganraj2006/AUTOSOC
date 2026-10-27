import { useQuery, useMutation } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface LogExplorerParams {
  category?: string;
  source_id?: string;
  severity?: string;
  source_ip?: string;
  destination_ip?: string;
  file_hash?: string;
  q?: string;
  start_time?: string;
  end_time?: string;
  sort_field?: "event_time" | "received_at" | "event_category" | "source_id";
  sort_direction?: "asc" | "desc";
  limit?: number;
  offset?: number;
}

export interface EventPage {
  total: number;
  events: SecurityEvent[];
  page: { total: number; limit: number; offset: number };
}

export interface SecurityEvent {
  [key: string]: unknown;
  normalized_event_id: string;
  event_time?: string;
  event_category: string;
  event_type: string;
  source_ip?: string;
  destination_ip?: string;
  event_outcome: string;
  event_action?: string;
  source_id?: string;
  source_type?: string;
  source_port?: number;
  destination_port?: number;
  protocol?: string;
  direction?: string;
  bytes_in?: number;
  bytes_out?: number;
  packets_in?: number;
  packets_out?: number;
  username?: string;
  user_id?: string;
  user_domain?: string;
  privilege_level?: string;
  hostname?: string;
  host_id?: string;
  host_ip?: string;
  operating_system?: string;
  process_name?: string;
  process_id?: number | string;
  command_line?: string;
  parent_process_name?: string;
  parent_process_id?: number | string;
  file_name?: string;
  file_path?: string;
  file_hashes?: Record<string, string>;
  asset_category?: string;
  asset_environment?: string;
  asset_criticality?: string;
  geo_country?: string;
  geo_city?: string;
  ip_reputation_status?: string;
  candidate_mitre_techniques?: string[];
  ingestion_id?: string;
  trace_id?: string;
  parser_name?: string;
  parser_version?: string;
  schema_version?: string;
  normalization_confidence?: number;
  normalization_warnings?: string[];
}

export interface EventUploadResult {
  total_rows: number;
  processed: number;
  failed: number;
  errors?: string[];
}

export interface AnomalyPrediction {
  event_id: string;
  is_anomaly: boolean;
  anomaly_score: number;
  model_score?: number;
}

export interface AnomalyDetectionResult {
  total_events: number;
  anomalies_detected: number;
  predictions?: AnomalyPrediction[];
}

export function useEvents(params: LogExplorerParams) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["events", params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== "") searchParams.append(key, String(value));
      });

      return fetchApi<EventPage>(`/events?${searchParams.toString()}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      });
    },
    enabled: status === "authenticated" && !!session?.accessToken,
  });
}

export function useEvent(eventId: string) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["events", eventId],
    queryFn: () =>
      fetchApi<SecurityEvent>(`/events/${eventId}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken && !!eventId,
  });
}

export function useUploadEvents() {
  const { data: session } = useSession();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      // fetchApi defaults to application/json if we don't override. 
      // We use standard fetch here to easily send FormData with correct boundary headers.
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${baseUrl}/events/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
        body: formData,
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(errorData?.detail || `Upload failed with status ${res.status}`);
      }
      return (await res.json()) as EventUploadResult;
    },
  });
}

export function useDetectAnomalies() {
  const { data: session } = useSession();

  return useMutation({
    mutationFn: async (limit: number = 100) => {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${baseUrl}/events/detect?limit=${limit}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(errorData?.detail || `Anomaly detection failed with status ${res.status}`);
      }
      return (await res.json()) as AnomalyDetectionResult;
    },
  });
}
