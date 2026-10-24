"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SessionProvider, signOut, useSession } from "next-auth/react";
import { usePathname } from "next/navigation";
import { ReactNode, useEffect, useRef, useState } from "react";

function ExpiredSessionRecovery({ children }: { children: ReactNode }) {
  const { data: session, status } = useSession();
  const pathname = usePathname();
  const hasStartedSignOut = useRef(false);

  useEffect(() => {
    if (
      status !== "authenticated" ||
      session?.error !== "RefreshAccessTokenError" ||
      hasStartedSignOut.current
    ) {
      return;
    }

    hasStartedSignOut.current = true;
    void signOut({ callbackUrl: `/login?callbackUrl=${encodeURIComponent(pathname)}` });
  }, [pathname, session?.error, status]);

  return children;
}

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60, // 1 minute
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <SessionProvider
      // Keycloak access tokens are intentionally short-lived. Refresh the
      // encrypted Auth.js session before client API polling can reuse one.
      refetchInterval={60}
      refetchWhenOffline={false}
    >
      <ExpiredSessionRecovery>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </ExpiredSessionRecovery>
    </SessionProvider>
  );
}
