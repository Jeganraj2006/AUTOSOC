import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";
import { PredictionResult } from "@/lib/api/predictions";

export function useLatestPrediction(incidentId: string) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["latest-prediction", incidentId],
    queryFn: () =>
      fetchApi<PredictionResult>(`/incidents/${incidentId}/predictions/latest`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken && !!incidentId,
  });
}

export function useAllPredictions(incidentId: string) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["predictions-history", incidentId],
    queryFn: () =>
      fetchApi<PredictionResult[]>(`/incidents/${incidentId}/predictions`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken && !!incidentId,
  });
}

export function useRecomputePrediction() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (incidentId: string) =>
      fetchApi<{ status: string; message: string }>(`/incidents/${incidentId}/predictions/recompute`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    onSuccess: (data, incidentId) => {
      queryClient.invalidateQueries({ queryKey: ["latest-prediction", incidentId] });
      queryClient.invalidateQueries({ queryKey: ["predictions-history", incidentId] });
    },
  });
}
