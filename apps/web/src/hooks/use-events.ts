import { useQuery, useMutation } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface LogExplorerParams {
  category?: string;
  source_ip?: string;
  limit?: number;
}

export function useEvents(params: LogExplorerParams) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["events", params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params.category) searchParams.append("category", params.category);
      if (params.source_ip) searchParams.append("source_ip", params.source_ip);
      if (params.limit) searchParams.append("limit", params.limit.toString());

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return fetchApi<{ total: number; events: any[] }>(`/events?${searchParams.toString()}`, {
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      fetchApi<any>(`/events/${eventId}`, {
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
      return res.json();
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
      return res.json();
    },
  });
}
