import { useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { fetchApi } from "@/lib/api";

export interface RuleMetadata {
  id: string;
  name: string;
  description?: string | null;
  rule_type: string;
  enabled: boolean;
  severity: string;
  version: number;
  mitre_references_json?: string | null;
  file_path?: string | null;
  created_at: string;
  updated_at: string;
}

export function useRules(skip = 0, limit = 100) {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["rules", skip, limit],
    queryFn: () =>
      fetchApi<RuleMetadata[]>(`/rules?skip=${skip}&limit=${limit}`, {
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      }),
    enabled: status === "authenticated" && !!session?.accessToken,
  });
}
