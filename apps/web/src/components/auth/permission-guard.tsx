"use client";

import { useMe } from "@/hooks/use-me";
import { ReactNode } from "react";
import { Skeleton } from "@/components/ui/skeleton";

interface PermissionGuardProps {
  children: ReactNode;
  allowedRoles?: string[];
  requireSuperuser?: boolean;
  fallback?: ReactNode;
}

export function PermissionGuard({
  children,
  allowedRoles,
  requireSuperuser,
  fallback = null,
}: PermissionGuardProps) {
  const { data: user, isLoading, isError } = useMe();

  if (isLoading) {
    return <Skeleton className="h-[200px] w-full rounded-xl" />;
  }

  if (isError || !user) {
    return fallback;
  }

  if (requireSuperuser && !user.is_superuser) {
    return fallback;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const hasRole = allowedRoles.some((role) => user.roles.includes(role));
    if (!hasRole && !user.is_superuser) {
      return fallback;
    }
  }

  return <>{children}</>;
}
