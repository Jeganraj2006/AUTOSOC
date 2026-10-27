"use client";

import { RefreshCw } from "lucide-react";
import { useRules } from "@/hooks/use-rules";
import { parseMitreReferences } from "@/lib/intelligence";
import { PageHeader } from "@/components/ui/page-header";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { SeverityBadge } from "@/components/ui/soc-indicators";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function RulesPage() {
  const { data: rules, isLoading, isError, isFetching, refetch } = useRules();
  if (isLoading) return <div className="space-y-6"><PageHeader title="Detection rules" description="Loading persisted rule configuration metadata." /><div className="soc-surface h-80 animate-pulse rounded-xl" /></div>;
  if (isError) return <div className="space-y-6"><PageHeader title="Detection rules" description="Review configured detection rules separately from their execution results." /><OperationalState kind="error" title="Rule metadata is unavailable" description="The rules API did not return a usable response. Retry the authenticated request." action={<RetryButton onClick={() => refetch()} disabled={isFetching} />} /></div>;
  return <div className="space-y-6"><PageHeader title="Detection rules" description="Configured rule inventory. This page does not represent rule executions or deployment status." actions={<Button variant="outline" onClick={() => refetch()} disabled={isFetching}><RefreshCw className={`mr-1.5 size-4 ${isFetching ? "animate-spin" : ""}`} />Refresh</Button>} /><section className="soc-table-wrap"><div className="border-b border-border px-4 py-3 text-sm text-muted-foreground">{rules?.length ?? 0} configured rules returned by the API.</div><Table><TableHeader><TableRow><TableHead>Rule</TableHead><TableHead>Category</TableHead><TableHead>Severity</TableHead><TableHead>Status</TableHead><TableHead>ATT&amp;CK</TableHead><TableHead>Updated</TableHead></TableRow></TableHeader><TableBody>{rules?.length ? rules.map((rule) => <TableRow key={rule.id}><TableCell><p className="font-medium text-foreground">{rule.name}</p><p className="mt-1 font-mono text-xs text-muted-foreground">{rule.id}</p></TableCell><TableCell>{rule.rule_type}</TableCell><TableCell><SeverityBadge severity={rule.severity} /></TableCell><TableCell>{rule.enabled ? <span className="text-emerald-600 dark:text-emerald-400">Enabled</span> : <span className="text-muted-foreground">Disabled</span>}</TableCell><TableCell className="font-mono text-xs text-muted-foreground">{parseMitreReferences(rule.mitre_references_json).join(", ") || "—"}</TableCell><TableCell className="text-sm text-muted-foreground">{new Date(rule.updated_at).toLocaleString()}</TableCell></TableRow>) : <TableRow><TableCell colSpan={6}><OperationalState kind="empty" title="No configured rules" description="The backend returned no rule metadata records." /></TableCell></TableRow>}</TableBody></Table></section><p className="text-xs text-muted-foreground">Rule creation, editing, validation, and deployment confirmation are not available in the current backend API and are intentionally not shown as controls.</p></div>;
}
