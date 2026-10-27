import { Activity, AlertTriangle, ClipboardCheck, Cpu, RadioTower, ShieldAlert } from "lucide-react";

type OperationsOverviewProps = {
  activeAlerts?: number;
  criticalIncidents?: number;
  sourceCount: number;
  healthStatus?: string;
  pendingApprovals?: number;
  completedInvestigations?: number;
  runningInvestigations?: number;
  failedInvestigations?: number;
  isLoading: boolean;
  unavailable: boolean;
};

function displayValue(value: number | undefined, isLoading: boolean, unavailable: boolean) {
  if (isLoading) return "Loading";
  if (unavailable || value === undefined) return "Unavailable";
  return value.toLocaleString();
}

export function OperationsOverview({
  activeAlerts,
  criticalIncidents,
  sourceCount,
  healthStatus,
  pendingApprovals,
  completedInvestigations,
  runningInvestigations,
  failedInvestigations,
  isLoading,
  unavailable,
}: OperationsOverviewProps) {
  const healthLabel = isLoading ? "Checking" : unavailable || !healthStatus ? "Unavailable" : healthStatus;
  const healthTone = healthLabel.toLowerCase() === "healthy" || healthLabel.toLowerCase() === "ok"
    ? "text-emerald-600 dark:text-emerald-400"
    : healthLabel === "Unavailable"
      ? "text-muted-foreground"
      : "text-amber-600 dark:text-amber-400";

  const cards = [
    {
      label: "Active alerts",
      value: displayValue(activeAlerts, isLoading, unavailable),
      detail: "Open alert records in the returned API window",
      icon: AlertTriangle,
      valueClassName: "text-amber-600 dark:text-amber-400",
    },
    {
      label: "Critical incidents",
      value: displayValue(criticalIncidents, isLoading, unavailable),
      detail: "Critical severity incidents in the returned API window",
      icon: ShieldAlert,
      valueClassName: "text-destructive",
    },
    {
      label: "Pipeline coverage",
      value: sourceCount.toLocaleString(),
      detail: "Data sources represented in the 24-hour telemetry summary",
      icon: RadioTower,
      valueClassName: "text-primary",
    },
    {
      label: "API health",
      value: healthLabel,
      detail: "Live status reported by the authenticated health endpoint",
      icon: Activity,
      valueClassName: healthTone,
    },
    {
      label: "Pending approvals",
      value: displayValue(pendingApprovals, isLoading, unavailable),
      detail: "Response approvals awaiting a decision",
      icon: ClipboardCheck,
      valueClassName: "text-amber-600 dark:text-amber-400",
    },
    {
      label: "Investigations",
      value: isLoading ? "Loading" : unavailable || completedInvestigations === undefined || runningInvestigations === undefined || failedInvestigations === undefined ? "Unavailable" : `${completedInvestigations} complete · ${runningInvestigations} running · ${failedInvestigations} failed`,
      detail: "Persisted AI investigation execution states",
      icon: Cpu,
      valueClassName: "text-violet-600 dark:text-violet-400",
    },
  ];

  return (
    <section aria-labelledby="operations-overview-heading" className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h2 id="operations-overview-heading" className="text-base font-semibold text-foreground">Operational posture</h2>
          <p className="mt-1 text-sm text-muted-foreground">Current state derived from live, authenticated application endpoints.</p>
        </div>
        <span className="text-xs text-muted-foreground">Counts are scoped to each endpoint&apos;s returned window.</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map(({ label, value, detail, icon: Icon, valueClassName }) => (
          <article key={label} className="soc-surface rounded-xl p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.08em] text-muted-foreground">{label}</p>
                <p className={`mt-2 text-2xl font-semibold tracking-[-0.03em] ${valueClassName}`}>{value}</p>
              </div>
              <Icon className="size-5 text-muted-foreground" aria-hidden="true" />
            </div>
            <p className="mt-3 text-xs leading-5 text-muted-foreground">{detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
