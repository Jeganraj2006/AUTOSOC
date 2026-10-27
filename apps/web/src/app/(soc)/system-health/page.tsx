"use client";

import { Activity, Database, Server, Bot } from "lucide-react";
import { useOperationalHealth } from "@/hooks/use-system-health";
import { PageHeader } from "@/components/ui/page-header";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { Button } from "@/components/ui/button";
import { healthStateLabel } from "@/lib/administration";

function healthTone(status: string) {
  if (status === "healthy") return "text-emerald-600 dark:text-emerald-400";
  if (status === "degraded") return "text-amber-600 dark:text-amber-400";
  if (status === "unknown") return "text-muted-foreground";
  return "text-destructive";
}

export default function SystemHealthPage() {
  const { data: health, isLoading, isError, isFetching, refetch, dataUpdatedAt } = useOperationalHealth();
  if (isLoading) return <div className="space-y-6"><PageHeader title="System health" description="Loading direct dependency checks and persisted operational telemetry." /><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{[1, 2, 3, 4, 5, 6].map((item) => <div key={item} className="soc-surface h-36 animate-pulse rounded-xl" />)}</div></div>;
  if (isError || !health) return <div className="space-y-6"><PageHeader title="System health" description="Direct dependency checks and durable worker telemetry." /><OperationalState kind="error" title="Operational status is unavailable" description="The authenticated health query did not return a usable response. Retry the request." action={<RetryButton onClick={() => refetch()} disabled={isFetching} />} /></div>;
  return <div className="space-y-6"><PageHeader title="System health" description="Direct dependency connectivity and persisted worker telemetry. Unknown is not treated as healthy." actions={<Button variant="outline" onClick={() => refetch()} disabled={isFetching}>Refresh</Button>} /><section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{health.components.map((component) => { const Icon = component.name.includes("Ollama") || component.name.includes("AI") ? Bot : component.name.includes("PostgreSQL") || component.name.includes("Redis") || component.name.includes("OpenSearch") || component.name.includes("storage") ? Database : component.name.includes("worker") ? Activity : Server; return <article key={component.name} className="soc-surface rounded-xl p-4"><div className="flex items-start justify-between gap-3"><div><p className="text-sm font-medium text-foreground">{component.name}</p><p className={`mt-2 text-lg font-semibold capitalize ${healthTone(component.status)}`}>{healthStateLabel(component.status)}</p></div><Icon className="size-5 text-muted-foreground" aria-hidden="true" /></div><p className="mt-3 text-xs leading-5 text-muted-foreground">{component.detail ?? "No detail reported."}</p>{component.last_successful_operation ? <p className="mt-2 text-xs text-muted-foreground">Last operation: {new Date(component.last_successful_operation).toLocaleString()}</p> : null}{component.model_identifier ? <p className="mt-2 font-mono text-xs text-muted-foreground">Model: {component.model_identifier}</p> : null}</article>; })}</section><section className="soc-surface rounded-xl p-5"><h2 className="font-semibold text-foreground">Telemetry limitations</h2><ul className="mt-3 space-y-2 text-sm leading-6 text-muted-foreground">{health.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul><p className="mt-4 text-xs text-muted-foreground">Checked: {dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleString() : "Not reported"}</p></section></div>;
}
