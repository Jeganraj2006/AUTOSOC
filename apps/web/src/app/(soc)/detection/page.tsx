"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Cpu, ExternalLink, RefreshCw, Search, ShieldCheck } from "lucide-react";
import { useDetectAnomalies, type AnomalyDetectionResult } from "@/hooks/use-events";
import { useRules, type RuleMetadata } from "@/hooks/use-rules";
import { filterRules, parseMitreReferences } from "@/lib/intelligence";
import { PageHeader } from "@/components/ui/page-header";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SeverityBadge } from "@/components/ui/soc-indicators";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

function RuleDetail({ rule }: { rule: RuleMetadata }) {
  const references = parseMitreReferences(rule.mitre_references_json);
  return (
    <section className="soc-surface rounded-xl p-5" aria-labelledby="rule-detail-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="rule-detail-heading" className="text-base font-semibold text-foreground">Rule detail</h2>
          <p className="mt-1 font-mono text-xs text-muted-foreground">{rule.id}</p>
        </div>
        <span className="text-xs text-muted-foreground">Updated {new Date(rule.updated_at).toLocaleString()}</span>
      </div>
      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(16rem,0.6fr)]">
        <div>
          <h3 className="font-medium text-foreground">{rule.name}</h3>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">{rule.description || "No rule description was provided by the metadata API."}</p>
        </div>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div><dt className="text-xs text-muted-foreground">Category</dt><dd className="mt-1 font-medium text-foreground">{rule.rule_type}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Version</dt><dd className="mt-1 font-medium text-foreground">{rule.version}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Status</dt><dd className="mt-1 font-medium text-foreground">{rule.enabled ? "Enabled" : "Disabled"}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Source file</dt><dd className="mt-1 break-all font-mono text-xs text-foreground">{rule.file_path || "Not supplied"}</dd></div>
        </dl>
      </div>
      <div className="mt-5 border-t border-border pt-4">
        <h3 className="text-sm font-medium text-foreground">Rule-derived ATT&amp;CK references</h3>
        {references.length ? <div className="mt-2 flex flex-wrap gap-2">{references.map((reference) => <span key={reference} className="rounded-md border border-border px-2 py-1 font-mono text-xs text-foreground">{reference}</span>)}</div> : <p className="mt-2 text-sm text-muted-foreground">No ATT&amp;CK mapping was returned for this rule.</p>}
      </div>
      <p className="mt-4 text-xs leading-5 text-muted-foreground">This metadata endpoint does not return rule execution counts, matching events, linked alerts, or related incidents.</p>
    </section>
  );
}

export default function DetectionPage() {
  const { data: rules, isLoading, isError, isFetching, refetch } = useRules();
  const detectMutation = useDetectAnomalies();
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("all");
  const [state, setState] = useState("all");
  const [selectedRuleId, setSelectedRuleId] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<AnomalyDetectionResult | null>(null);

  const filteredRules = useMemo(() => filterRules(rules ?? [], query, severity, state), [rules, query, severity, state]);
  const selectedRule = rules?.find((rule) => rule.id === selectedRuleId);
  const anomalies = detectionResult?.predictions?.filter((item) => item.is_anomaly) ?? [];

  if (isLoading) {
    return <div className="space-y-6"><PageHeader title="Detection intelligence" description="Loading persisted detection-rule metadata." /><div className="soc-surface h-80 animate-pulse rounded-xl" /></div>;
  }
  if (isError) {
    return <div className="space-y-6"><PageHeader title="Detection intelligence" description="Review rule configuration separately from real-time anomaly execution." /><OperationalState kind="error" title="Detection rules are unavailable" description="The rules metadata endpoint did not return a usable response. Retry after checking your authenticated API connection." action={<RetryButton onClick={() => refetch()} disabled={isFetching} />} /></div>;
  }

  return (
    <div className="space-y-6 pb-10">
      <PageHeader title="Detection intelligence" description="Review persisted rule configuration separately from execution results and generated security records." actions={<Button variant="outline" onClick={() => refetch()} disabled={isFetching}><RefreshCw className={`mr-1.5 size-4 ${isFetching ? "animate-spin" : ""}`} />Refresh rules</Button>} />
      <section className="grid gap-3 sm:grid-cols-3" aria-label="Detection rule summary">
        <div className="soc-surface rounded-xl p-4"><p className="text-xs font-medium text-muted-foreground">Loaded rules</p><p className="mt-2 text-2xl font-semibold tabular-nums text-foreground">{rules?.length ?? 0}</p></div>
        <div className="soc-surface rounded-xl p-4"><p className="text-xs font-medium text-muted-foreground">Enabled rules</p><p className="mt-2 text-2xl font-semibold tabular-nums text-emerald-600 dark:text-emerald-400">{rules?.filter((rule) => rule.enabled).length ?? 0}</p></div>
        <div className="soc-surface rounded-xl p-4"><p className="text-xs font-medium text-muted-foreground">Latest anomaly run</p><p className="mt-2 text-2xl font-semibold tabular-nums text-foreground">{detectionResult ? detectionResult.anomalies_detected : "Not run"}</p><p className="mt-1 text-xs text-muted-foreground">Only populated after a user-run evaluation.</p></div>
      </section>
      <section className="soc-surface flex flex-wrap items-end gap-3 rounded-xl p-4" aria-label="Rule filters">
        <label className="min-w-52 flex-1"><span className="text-xs font-medium text-muted-foreground">Find a returned rule</span><span className="relative mt-1 block"><Search className="pointer-events-none absolute left-3 top-2.5 size-4 text-muted-foreground" /><Input value={query} onChange={(event) => setQuery(event.target.value)} className="pl-9" placeholder="Name, ID, category, or description" /></span></label>
        <label><span className="text-xs font-medium text-muted-foreground">Severity</span><Select value={severity} onValueChange={(value) => value && setSeverity(value)}><SelectTrigger className="mt-1 w-36"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">All</SelectItem><SelectItem value="critical">Critical</SelectItem><SelectItem value="high">High</SelectItem><SelectItem value="medium">Medium</SelectItem><SelectItem value="low">Low</SelectItem></SelectContent></Select></label>
        <label><span className="text-xs font-medium text-muted-foreground">State</span><Select value={state} onValueChange={(value) => value && setState(value)}><SelectTrigger className="mt-1 w-36"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">All</SelectItem><SelectItem value="enabled">Enabled</SelectItem><SelectItem value="disabled">Disabled</SelectItem></SelectContent></Select></label>
        <p className="basis-full text-xs text-muted-foreground">Filtering is local to the {rules?.length ?? 0} rule records returned by the API; the rules API supports only skip and limit.</p>
      </section>
      <section className="soc-table-wrap" aria-labelledby="rules-heading"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3"><div><h2 id="rules-heading" className="font-semibold text-foreground">Rule inventory</h2><p className="mt-1 text-xs text-muted-foreground">{filteredRules.length} matching metadata records</p></div><Button onClick={() => detectMutation.mutate(100, { onSuccess: setDetectionResult })} disabled={detectMutation.isPending}><Cpu className={`mr-1.5 size-4 ${detectMutation.isPending ? "animate-spin" : ""}`} />{detectMutation.isPending ? "Running evaluation" : "Run anomaly evaluation"}</Button></div>{detectMutation.isError ? <div className="border-b border-border p-4 text-sm text-destructive">The anomaly evaluation did not complete. Verify event availability and your role, then retry.</div> : null}<Table><TableHeader><TableRow><TableHead>Rule</TableHead><TableHead>Category</TableHead><TableHead>Severity</TableHead><TableHead>Status</TableHead><TableHead>ATT&amp;CK</TableHead><TableHead className="text-right">Detail</TableHead></TableRow></TableHeader><TableBody>{filteredRules.length ? filteredRules.map((rule) => <TableRow key={rule.id}><TableCell><button type="button" onClick={() => setSelectedRuleId(rule.id)} className="text-left font-medium text-foreground hover:underline">{rule.name}<span className="mt-1 block font-mono text-xs text-muted-foreground">{rule.id}</span></button></TableCell><TableCell>{rule.rule_type}</TableCell><TableCell><SeverityBadge severity={rule.severity} /></TableCell><TableCell><span className={rule.enabled ? "text-emerald-600 dark:text-emerald-400" : "text-muted-foreground"}>{rule.enabled ? "Enabled" : "Disabled"}</span></TableCell><TableCell className="font-mono text-xs text-muted-foreground">{parseMitreReferences(rule.mitre_references_json).join(", ") || "—"}</TableCell><TableCell className="text-right"><Button variant="ghost" size="icon" onClick={() => setSelectedRuleId(rule.id)} aria-label={`View ${rule.name} detail`}><ExternalLink className="size-4" /></Button></TableCell></TableRow>) : <TableRow><TableCell colSpan={6}><OperationalState kind="empty" title="No rules match these filters" description="Clear or broaden the local filters to inspect the available rule metadata." /></TableCell></TableRow>}</TableBody></Table></section>
      {selectedRule ? <RuleDetail rule={selectedRule} /> : null}
      {detectionResult ? <section className="soc-surface rounded-xl p-5" aria-labelledby="anomaly-results-heading"><div className="flex flex-wrap items-start justify-between gap-3"><div><h2 id="anomaly-results-heading" className="font-semibold text-foreground">Latest anomaly evaluation</h2><p className="mt-1 text-sm text-muted-foreground">{detectionResult.total_events} events evaluated; {detectionResult.anomalies_detected} results flagged by the model.</p></div><span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground"><AlertTriangle className="size-4 text-amber-600 dark:text-amber-400" />Execution output, not rule matches</span></div>{anomalies.length ? <div className="mt-4 space-y-2">{anomalies.map((item) => <div key={item.event_id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border p-3"><div><p className="font-mono text-sm text-foreground">{item.event_id}</p><p className="mt-1 text-xs text-muted-foreground">Anomaly score: {item.anomaly_score}{item.model_score !== undefined ? ` · model score: ${item.model_score}` : ""}</p></div><Link className="inline-flex h-9 items-center rounded-md border border-border px-3 text-sm font-medium text-foreground hover:bg-muted" href={`/events/${encodeURIComponent(item.event_id)}`}>Open event<ExternalLink className="ml-1.5 size-3.5" /></Link></div>)}</div> : <div className="mt-4 flex items-center gap-2 rounded-lg border border-border p-4 text-sm text-muted-foreground"><ShieldCheck className="size-4 text-emerald-600 dark:text-emerald-400" />No anomalies were returned by this evaluation.</div>}</section> : null}
    </div>
  );
}
