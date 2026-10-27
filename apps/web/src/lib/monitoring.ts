export type RoleAwareUser = {
  is_superuser?: boolean;
  roles: string[];
};

export function buildEventQuery(category: string, sourceIp: string, limit: number) {
  return {
    category: category === "all" ? undefined : category,
    source_ip: sourceIp.trim() === "" ? undefined : sourceIp.trim(),
    limit,
  };
}

export function isActiveAlertStatus(status: string) {
  return !["resolved", "closed", "false_positive"].includes(status.toLowerCase());
}

export function canManageTriage(user: RoleAwareUser | undefined) {
  return Boolean(
    user?.is_superuser ||
      user?.roles.some((role) => ["admin", "administrator", "soc_analyst", "security_analyst"].includes(role)),
  );
}

export function incidentHref(incidentId: string) {
  return `/incidents/${encodeURIComponent(incidentId)}`;
}

export function canExecuteApprovedDryRun(status: string, canExecute: boolean) {
  return canExecute && status === "approved";
}
