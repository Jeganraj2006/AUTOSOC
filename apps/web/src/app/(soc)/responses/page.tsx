"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { ResponsePanel } from "@/components/incidents/response-panel";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useGlobalResponses } from "@/hooks/use-responses";

const PAGE_SIZE = 25;

export default function ResponsesPage() {
  const [status, setStatus] = useState("all");
  const [incidentId, setIncidentId] = useState("");
  const [offset, setOffset] = useState(0);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const params = {
    status_filter: status === "all" ? undefined : status,
    incident_id: incidentId.trim() || undefined,
    limit: PAGE_SIZE,
    offset,
  };
  const { data, isError, isLoading, isFetching, refetch } = useGlobalResponses(params);
  const proposals = data?.proposals ?? [];

  const applyFilters = () => setOffset(0);
  if (isError) {
    return <div className="space-y-6"><PageHeader title="Response management" description="Review persisted response proposals, approvals, and validated dry-run results." /><OperationalState kind="error" title="Response records are unavailable" description="The authenticated response query failed. Verify your session and retry." action={<RetryButton onClick={() => refetch()} disabled={isFetching} />} /></div>;
  }

  return (
    <div className="space-y-6 pb-10">
      <PageHeader title="Response management" description="Server-paged proposal history with persisted review and execution state. Validated dry runs never perform external containment." />
      <section className="soc-surface flex flex-wrap items-end gap-3 rounded-xl p-4" aria-label="Response filters">
        <div className="space-y-1.5"><label className="text-xs font-medium text-muted-foreground" htmlFor="response-status">Proposal status</label><Select value={status} onValueChange={(value) => { setStatus(value ?? "all"); setOffset(0); }}><SelectTrigger id="response-status" className="w-44"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">All statuses</SelectItem><SelectItem value="proposed">Proposed</SelectItem><SelectItem value="pending_review">Pending review</SelectItem><SelectItem value="approved">Approved</SelectItem><SelectItem value="rejected">Rejected</SelectItem><SelectItem value="executed">Executed</SelectItem></SelectContent></Select></div>
        <div className="space-y-1.5"><label className="text-xs font-medium text-muted-foreground" htmlFor="response-incident">Incident ID</label><Input id="response-incident" value={incidentId} onChange={(event) => setIncidentId(event.target.value)} placeholder="Exact incident UUID" className="w-72 font-mono text-xs" /></div>
        <Button type="button" variant="outline" onClick={applyFilters}>Apply filters</Button>
      </section>
      <section className="soc-surface overflow-hidden rounded-xl" aria-labelledby="response-history-heading">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3"><div><h2 id="response-history-heading" className="font-semibold text-foreground">Proposal history</h2><p className="mt-1 text-xs text-muted-foreground">{isLoading ? "Loading persisted proposals…" : `${data?.page.total ?? 0} matching proposal${data?.page.total === 1 ? "" : "s"}`}</p></div><p className="text-xs text-muted-foreground">Validated only — no external action performed.</p></div>
        {proposals.length ? <div className="divide-y divide-border">{proposals.map((proposal) => { const decision = proposal.approvals.at(-1)?.decision ?? "not requested"; const execution = proposal.executions.at(-1); return <button key={proposal.id} type="button" onClick={() => setSelectedIncidentId(proposal.incident_id)} className="grid w-full gap-2 px-4 py-3 text-left transition-colors hover:bg-muted/60 md:grid-cols-[minmax(0,1.5fr)_repeat(3,minmax(0,0.8fr))]"><span><span className="block truncate text-sm font-medium text-foreground">{proposal.action_type} · {proposal.target_reference}</span><span className="mt-1 block truncate font-mono text-xs text-muted-foreground">{proposal.id}</span></span><span className="text-xs text-muted-foreground"><strong className="block font-medium text-foreground">{proposal.status.replaceAll("_", " ")}</strong>Proposal state</span><span className="text-xs text-muted-foreground"><strong className="block font-medium text-foreground">{decision}</strong>Review state</span><span className="text-xs text-muted-foreground"><strong className="block font-medium text-foreground">{execution?.status ?? "Not executed"}</strong>{execution ? "Persisted execution" : "No execution record"}</span></button>; })}</div> : <OperationalState kind="empty" title="No proposals match this query" description="Change the server-side filters or create a proposal from an incident." action={status !== "all" || incidentId ? <Button variant="outline" onClick={() => { setStatus("all"); setIncidentId(""); setOffset(0); }}>Clear filters</Button> : undefined} />}
        <div className="flex items-center justify-end gap-2 border-t border-border px-4 py-3"><Button variant="outline" size="sm" disabled={offset === 0 || isFetching} onClick={() => setOffset((value) => Math.max(0, value - PAGE_SIZE))}><ChevronLeft className="mr-1 size-4" />Previous</Button><Button variant="outline" size="sm" disabled={!data || offset + PAGE_SIZE >= data.page.total || isFetching} onClick={() => setOffset((value) => value + PAGE_SIZE)}>Next<ChevronRight className="ml-1 size-4" /></Button></div>
      </section>
      {selectedIncidentId ? <section className="border-t border-border pt-6"><div className="mb-3 flex items-center justify-between gap-3"><div><h2 className="font-semibold text-foreground">Incident response actions</h2><p className="mt-1 font-mono text-xs text-muted-foreground">{selectedIncidentId}</p></div><Button variant="ghost" size="sm" onClick={() => setSelectedIncidentId(null)}>Close actions</Button></div><ResponsePanel incidentId={selectedIncidentId} /></section> : null}
    </div>
  );
}
