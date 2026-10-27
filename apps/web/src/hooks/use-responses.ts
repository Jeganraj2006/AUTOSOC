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
  impact: string;
  reversibility: string;
  approval_required?: boolean;
  rollback_available?: boolean;
  status: "proposed" | "pending_review" | "approved" | "rejected" | "executed";
  created_by: string;
  created_at: string;
}

export interface ResponseApproval {
  id: string;
  recommendation_id: string;
  incident_id: string;
  requested_by: string;
  reviewer?: string;
  decision: "pending" | "approved" | "rejected";
  reason?: string;
}

export interface ResponseExecution {
  id: string;
  recommendation_id: string;
  approval_id?: string;
  mode: "dry_run" | "simulation" | "analyst_approved_execution";
  status: string;
  executor?: string;
  started_at?: string;
  completed_at?: string;
  idempotency_key?: string;
  verification_status?: string;
}

export interface GlobalResponseRecommendation extends ResponseRecommendation {
  approvals: ResponseApproval[];
  executions: ResponseExecution[];
}

export interface GlobalResponsePage {
  proposals: GlobalResponseRecommendation[];
  page: { total: number; limit: number; offset: number };
}

export interface GlobalResponsesParams {
  status_filter?: string;
  incident_id?: string;
  creator?: string;
  approval_status?: "pending" | "approved" | "rejected" | "expired" | "cancelled";
  sort_field?: "created_at" | "status" | "priority";
  sort_direction?: "asc" | "desc";
  limit?: number;
  offset?: number;
}

export function useGlobalResponses(params: GlobalResponsesParams = {}) {
  const { data: session, status } = useSession();
  return useQuery({
    queryKey: ["responses", "global", params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== "") searchParams.append(key, String(value));
      });
      return fetchApi<GlobalResponsePage>(`/responses?${searchParams.toString()}`, {
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      });
    },
    enabled: status === "authenticated" && !!session?.accessToken,
  });
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
      impact,
      reversibility,
    }: {
      incidentId: string;
      action_type: string;
      playbook_id: string;
      target_reference: string;
      rationale: string;
      impact: string;
      reversibility: string;
    }) => {
      return fetchApi<ResponseRecommendation>(`/incidents/${incidentId}/responses`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          incident_id: incidentId,
          source: "analyst_playbook",
          action_type,
          playbook_id,
          target_type: action_type,
          target_reference,
          rationale,
          expected_benefit: "Reduce the identified incident exposure through a human-reviewed response.",
          evidence_references: [],
          impact,
          reversibility,
        }),
      });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["responses", variables.incidentId] });
    },
  });
}

export function useRequestResponseApproval() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recommendationId: string) =>
      fetchApi<ResponseApproval>(`/responses/${recommendationId}/request-approval`, {
        method: "POST",
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["responses"] }),
  });
}

export function useDecideResponseApproval() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ recommendationId, decision }: { recommendationId: string; decision: "approved" | "rejected" }) =>
      fetchApi<ResponseApproval>(`/responses/${recommendationId}/approve`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ decision, reason: `Decision recorded through the AutoSOC response review workflow: ${decision}.` }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["responses"] }),
  });
}

export function useDryRunResponse() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recommendationId: string) =>
      fetchApi<ResponseExecution>(`/responses/${recommendationId}/execute`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ recommendation_id: recommendationId, mode: "dry_run" }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["responses"] }),
  });
}
