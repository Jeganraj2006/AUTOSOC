import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface IncidentResponse {
  id: string;
  title: string;
  description?: string;
  severity: string;
  status: string;
  risk_score: number;
  created_at: string;
  updated_at: string;
  first_seen?: string;
  last_seen?: string;
  assignee_id?: string;
  alert_count: number;
  event_count: number;
  primary_entities?: unknown[];
  tags?: string[];
  correlation_rule_ids?: string[];
  candidate_mitre_references?: string[];
  resolution_summary?: string;
  closure_reason?: string;
  false_positive_reason?: string;
}

export interface IncidentNoteResponse {
  id: string;
  incident_id: string;
  author_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface AgentResultSection {
  findings?: string[];
  confidence?: string;
  evidence_references?: string[];
  retrieved_source_references?: string[];
  assumptions?: string[];
  uncertainties?: string[];
  recommendations?: string[];
}

export interface AgentResult {
  agent_name: string;
  execution_id: string;
  incident_id: string;
  status: string;
  generated_at: string;
  model_name: string;
  prompt_version: string;
  schema_version: string;
  
  detection_verification?: AgentResultSection;
  investigation?: AgentResultSection;
  threat_intelligence?: AgentResultSection;
  risk_assessment?: AgentResultSection;
  prediction_analysis?: AgentResultSection;
  response_recommendation?: AgentResultSection;
  reporting?: Record<string, unknown>;
}

export interface AgentExecutionResponse {
  id: string;
  incident_id: string;
  workflow_type: string;
  status: string;
  requested_by?: string;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  current_step?: string;
  steps_completed: number;
  retry_count: number;
  node_statuses?: Record<string, string>;
  node_timestamps?: Record<string, string>;
  model_provider?: string;
  model_name?: string;
  model_version?: string;
  prompt_version?: string;
  tool_calls_count: number;
  duration_seconds?: number;
  result_data?: AgentResult;
  failure_reason?: string;
  error_info?: Record<string, unknown>;
  evidence_references?: string[];
  trace_id?: string;
}

export function useIncidents(skip = 0, limit = 100) {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["incidents", skip, limit],
    queryFn: () =>
      fetchApi<IncidentResponse[]>(`/incidents/?skip=${skip}&limit=${limit}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: authStatus === "authenticated" && !!session?.accessToken,
  });
}

export function useIncident(incidentId: string) {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["incidents", incidentId],
    queryFn: () =>
      fetchApi<IncidentResponse>(`/incidents/${incidentId}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: authStatus === "authenticated" && !!session?.accessToken && !!incidentId,
  });
}

export function useUpdateIncidentStatus() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      incidentId,
      status,
      reason,
    }: {
      incidentId: string;
      status: string;
      reason?: string;
    }) => {
      const searchParams = new URLSearchParams();
      searchParams.append("status", status);
      if (reason) {
        searchParams.append("reason", reason);
      }
      return fetchApi<IncidentResponse>(
        `/incidents/${incidentId}/status?${searchParams.toString()}`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${session?.accessToken}`,
          },
        }
      );
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.setQueryData(["incidents", variables.incidentId], data);
    },
  });
}

export function useIncidentNotes(incidentId: string) {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["incident-notes", incidentId],
    queryFn: () =>
      fetchApi<IncidentNoteResponse[]>(`/incidents/${incidentId}/notes`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: authStatus === "authenticated" && !!session?.accessToken && !!incidentId,
  });
}

export function useAddIncidentNote() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, content }: { incidentId: string; content: string }) =>
      fetchApi<IncidentNoteResponse>(`/incidents/${incidentId}/notes`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
      }),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["incident-notes", variables.incidentId] });
    },
  });
}

export function useIncidentAgents(incidentId: string) {
  const { data: session, status: authStatus } = useSession();

  return useQuery({
    queryKey: ["incident-agents", incidentId],
    queryFn: () =>
      fetchApi<AgentExecutionResponse[]>(`/${incidentId}/agents`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: authStatus === "authenticated" && !!session?.accessToken && !!incidentId,
  });
}

export function useTriggerIncidentAgent() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, workflowType }: { incidentId: string; workflowType: string }) =>
      fetchApi<AgentExecutionResponse>(`/${incidentId}/agents/investigate`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ workflow_type: workflowType, incident_id: incidentId }),
      }),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["incident-agents", variables.incidentId] });
    },
  });
}
