"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { PageHeader } from "@/components/ui/page-header";
import { useAuditRecords } from "@/hooks/use-audit";
import { useState } from "react";

const PAGE_SIZE = 25;

export default function AuditPage() {
  const [action, setAction] = useState("");
  const [actor, setActor] = useState("");
  const [offset, setOffset] = useState(0);
  const { data, isLoading, isError, isFetching, refetch } = useAuditRecords({ action: action || undefined, actor: actor || undefined, limit: PAGE_SIZE, offset });
  if (isError) return <div className="space-y-6"><PageHeader title="Audit activity" description="Read-only evidence of authenticated AutoSOC actions." /><OperationalState kind="error" title="Audit history is unavailable" description="The audited-records query failed. Verify that your session includes audit access, then retry." action={<RetryButton onClick={() => refetch()} disabled={isFetching} />} /></div>;

  return <div className="space-y-6"><PageHeader title="Audit activity" description="Read-only, server-paged records. Sensitive metadata is redacted by the API before delivery to the browser." /><section className="soc-surface flex flex-wrap items-end gap-3 rounded-xl p-4"><div className="space-y-1.5"><label htmlFor="audit-action" className="text-xs font-medium text-muted-foreground">Exact action</label><Input id="audit-action" value={action} onChange={(event) => { setAction(event.target.value); setOffset(0); }} placeholder="response.approval_approved" className="w-64" /></div><div className="space-y-1.5"><label htmlFor="audit-actor" className="text-xs font-medium text-muted-foreground">Exact actor ID</label><Input id="audit-actor" value={actor} onChange={(event) => { setActor(event.target.value); setOffset(0); }} placeholder="Optional actor identifier" className="w-60" /></div><Button variant="outline" onClick={() => { setAction(""); setActor(""); setOffset(0); }}>Clear</Button></section><section className="soc-surface overflow-hidden rounded-xl"><div className="border-b border-border px-4 py-3"><h2 className="font-semibold text-foreground">Recorded activity</h2><p className="mt-1 text-xs text-muted-foreground">{isLoading ? "Loading audit evidence…" : `${data?.page.total ?? 0} matching record${data?.page.total === 1 ? "" : "s"}`}</p></div>{data?.records.length ? <div className="divide-y divide-border">{data.records.map((record) => <article key={record.id} className="grid gap-2 px-4 py-3 md:grid-cols-[minmax(12rem,0.9fr)_minmax(0,1.5fr)_minmax(0,1fr)]"><div><p className="text-sm font-medium text-foreground">{record.action}</p><p className="mt-1 text-xs text-muted-foreground">{formatDistanceToNow(new Date(record.timestamp), { addSuffix: true })}</p></div><div><p className="text-xs text-muted-foreground">{record.resource_type}</p><p className="mt-1 truncate font-mono text-xs text-foreground">{record.resource_id ?? "No resource identifier"}</p></div><div><p className="text-xs text-muted-foreground">Actor</p><p className="mt-1 truncate text-sm text-foreground">{record.actor_name ?? record.actor_id}</p><p className="mt-1 text-xs text-muted-foreground">Result: {record.result}</p></div></article>)}</div> : <OperationalState kind="empty" title="No audit records match this query" description="Audit history is immutable. Change the exact filters or perform an authorized workflow to create a new record." />}<div className="flex justify-end gap-2 border-t border-border px-4 py-3"><Button variant="outline" size="sm" disabled={offset === 0 || isFetching} onClick={() => setOffset((value) => Math.max(0, value - PAGE_SIZE))}><ChevronLeft className="mr-1 size-4" />Previous</Button><Button variant="outline" size="sm" disabled={!data || offset + PAGE_SIZE >= data.page.total || isFetching} onClick={() => setOffset((value) => value + PAGE_SIZE)}>Next<ChevronRight className="ml-1 size-4" /></Button></div></section></div>;
}
