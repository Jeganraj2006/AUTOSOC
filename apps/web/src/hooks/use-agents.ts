import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";
import { AgentExecutionResponse } from "./use-incidents";

export function useAgentExecution(executionId: string) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["agent-execution", executionId],
    queryFn: () =>
      fetchApi<AgentExecutionResponse>(`/agent-executions/${executionId}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken && !!executionId,
  });
}

export function useCancelAgentExecution() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (executionId: string) =>
      fetchApi<{ message: string }>(`/agent-executions/${executionId}/cancel`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    onSuccess: (data, executionId) => {
      queryClient.invalidateQueries({ queryKey: ["agent-execution", executionId] });
      queryClient.invalidateQueries({ queryKey: ["incident-agents"] });
    },
  });
}
