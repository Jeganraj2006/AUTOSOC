import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: string[];
}

export function useMe() {
  const { data: session, status } = useSession();

  return useQuery({
    queryKey: ["me"],
    queryFn: () =>
      fetchApi<UserProfile>("/auth/me", {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      }),
    enabled: status === "authenticated" && !!session?.accessToken,
    staleTime: 1000 * 60 * 5,
  });
}