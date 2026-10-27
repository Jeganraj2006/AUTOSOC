import type { RoleAwareUser } from "@/lib/monitoring";

export function canManageDataSources(user: RoleAwareUser | undefined) {
  return Boolean(user?.is_superuser || user?.roles.some((role) => role === "admin" || role === "administrator"));
}

export function healthStateLabel(status?: string) {
  const value = status?.toLowerCase();
  if (value === "healthy" || value === "ok") return "Healthy";
  if (value === "degraded") return "Degraded";
  if (!value) return "Not reported";
  return "Unavailable";
}

export function responseStatusLabel(status: string) {
  return status.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
