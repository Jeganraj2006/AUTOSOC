import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface ResponseRecommendation {
  id: string;
  incident_id: string;
  action_type: string;
  playbook_id: string;
  target_reference: string;
  rationale: string;
  risk_assessment: string;
  status: "proposed" | "pending_review" | "approved" | "rejected" | "executed";
  created_by: string;
  created_at: string;
}

export function useResponseRecommendations(incidentId: string) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["responses", incidentId],
    queryFn: () =>
      fetchApi<ResponseRecommendation[]>(`/incidents/${incidentId}/responses`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken && !!incidentId,
  });
}

export function useCreateResponseRecommendation() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      incidentId,
      action_type,
      playbook_id,
      target_reference,
      rationale,
      risk_assessment,
    }: {
      incidentId: string;
      action_type: string;
      playbook_id: string;
      target_reference: string;
      rationale: string;
      risk_assessment: string;
    }) => {
      return fetchApi<ResponseRecommendation>(`/incidents/${incidentId}/responses`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          incident_id: incidentId,
          action_type,
          playbook_id,
          target_reference,
          rationale,
          risk_assessment,
        }),
      });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["responses", variables.incidentId] });
    },
  });
}
