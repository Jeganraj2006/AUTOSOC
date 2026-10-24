"use client";

import React from "react";
import { useEvent } from "@/hooks/use-events";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Copy, AlertTriangle, ShieldCheck, FileJson, Check, AlertCircle, RefreshCw } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      className="h-6 w-6 text-zinc-500 hover:text-zinc-100"
      onClick={handleCopy}
      title="Copy to clipboard"
    >
      {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
    </Button>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card className="bg-zinc-950 border-zinc-900 shadow-none">
      <CardHeader className="pb-3 border-b border-zinc-900">
        <CardTitle className="text-xs font-semibold text-zinc-400 uppercase tracking-wider font-mono">{title}</CardTitle>
      </CardHeader>
      <CardContent className="pt-4 space-y-2 text-xs font-mono">{children}</CardContent>
    </Card>
  );
}

function Field({ label, value, copyable = false, mono = false }: { label: string; value: unknown; copyable?: boolean; mono?: boolean }) {
  if (value === undefined || value === null || value === "") return null;
  const displayValue = String(value);

  // Auto-redaction safeguard for frontend if backend missed it
  if (label.toLowerCase().includes("password") || label.toLowerCase().includes("secret") || label.toLowerCase().includes("token")) {
    return (
      <div className="flex flex-col sm:flex-row sm:items-start py-1">
        <span className="w-48 text-zinc-500 font-semibold shrink-0">{label}:</span>
        <span className="text-red-500 italic font-mono">[REDACTED]</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col sm:flex-row sm:items-start py-1 group">
      <span className="w-48 text-zinc-500 font-semibold shrink-0">{label}:</span>
      <span className={`text-zinc-300 break-all ${mono ? "font-mono text-zinc-400" : ""}`}>
        {displayValue}
      </span>
      {copyable && (
        <div className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <CopyButton value={displayValue} />
        </div>
      )}
    </div>
  );
}

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.eventId as string;

  const { data: event, isLoading, isError, refetch } = useEvent(eventId);

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="space-y-6 font-mono">
        <div className="flex items-center gap-3 border-b border-zinc-900 pb-4">
          <Skeleton className="h-8 w-8 bg-zinc-900" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-7 w-96 bg-zinc-900" />
            <Skeleton className="h-3 w-48 bg-zinc-900" />
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-[250px] rounded-lg bg-zinc-900" />
          <Skeleton className="h-[250px] rounded-lg bg-zinc-900" />
        </div>
      </div>
    );
  }

  // 2. Error State
  if (isError || !event) {
    return (
      <div className="flex h-[400px] flex-col items-center justify-center rounded-lg border border-red-900/40 bg-red-950/10 p-6 text-center font-mono">
        <AlertCircle className="mb-4 h-12 w-12 text-red-500" />
        <h3 className="text-lg font-bold text-red-400">Event Not Found</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-2 mb-6">
          The requested event record was not found in the OpenSearch indexes.
        </p>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => router.push("/events")}
            variant="outline"
            className="border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-xs"
          >
            Back to Log Explorer
          </Button>
          <Button
            onClick={() => refetch()}
            className="bg-red-950/40 border border-red-900/60 hover:bg-red-900/30 text-red-400 text-xs"
          >
            <RefreshCw className="h-3.5 w-3.5 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-mono pb-12">
      {/* Header Block */}
      <div className="flex items-center gap-4 border-b border-zinc-900 pb-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => router.push("/events")}
          className="h-8 w-8 bg-zinc-950 border-zinc-900 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Event Details</h2>
          <p className="text-xs text-zinc-500">ID: {event.normalized_event_id}</p>
        </div>
      </div>

      {/* Details Sections Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        <Section title="Overview">
          <Field label="Timestamp" value={event.event_time ? new Date(event.event_time).toLocaleString() : "-"} />
          <Field label="Relative Time" value={event.event_time ? formatDistanceToNow(new Date(event.event_time), { addSuffix: true }) : "-"} />
          <Field label="Category" value={event.event_category} />
          <Field label="Type" value={event.event_type} />
          <Field label="Action" value={event.event_action} />
          <Field label="Outcome" value={event.event_outcome} />
          <Field label="Source name" value={event.source_id} />
          <Field label="Source type" value={event.source_type} />
        </Section>

        <Section title="Network context">
          <Field label="Source IP" value={event.source_ip} copyable mono />
          <Field label="Source port" value={event.source_port} mono />
          <Field label="Destination IP" value={event.destination_ip} copyable mono />
          <Field label="Destination port" value={event.destination_port} mono />
          <Field label="Protocol" value={event.protocol} />
          <Field label="Direction" value={event.direction} />
          <Field label="Bytes In" value={event.bytes_in} />
          <Field label="Bytes Out" value={event.bytes_out} />
          <Field label="Packets In" value={event.packets_in} />
          <Field label="Packets Out" value={event.packets_out} />
        </Section>

        <Section title="Identity">
          <Field label="Username" value={event.username} copyable />
          <Field label="User ID" value={event.user_id} copyable mono />
          <Field label="Domain" value={event.user_domain} />
          <Field label="Privilege Level" value={event.privilege_level} />
        </Section>

        <Section title="Host">
          <Field label="Hostname" value={event.hostname} copyable />
          <Field label="Host ID" value={event.host_id} copyable mono />
          <Field label="Host IP" value={event.host_ip} copyable mono />
          <Field label="OS" value={event.operating_system} />
        </Section>

        <Section title="Process & File">
          <Field label="Process Name" value={event.process_name} copyable />
          <Field label="PID" value={event.process_id} mono />
          <Field label="Command Line" value={event.command_line} copyable mono />
          <Field label="Parent process" value={event.parent_process_name} />
          <Field label="Parent PID" value={event.parent_process_id} mono />
          <Field label="File name" value={event.file_name} />
          <Field label="File path" value={event.file_path} copyable mono />
          {event.file_hashes && Object.entries(event.file_hashes).map(([k, v]) => (
            <Field key={k} label={`Hash (${k.toUpperCase()})`} value={v} copyable mono />
          ))}
        </Section>

        <Section title="Threat Context & Enrichment">
          <div className="mb-4 flex items-center gap-2 rounded border border-indigo-900/60 bg-indigo-950/20 p-2 text-xs text-indigo-400 font-mono">
            <ShieldCheck className="h-4 w-4 shrink-0 text-indigo-400" />
            <p>Heuristic classification context only</p>
          </div>
          <Field label="Asset Category" value={event.asset_category} />
          <Field label="Asset Environment" value={event.asset_environment} />
          <Field label="Asset Criticality" value={event.asset_criticality} />
          <Field label="Geo Country" value={event.geo_country} />
          <Field label="Geo City" value={event.geo_city} />
          <Field label="IP Reputation" value={event.ip_reputation_status} />
          {event.candidate_mitre_techniques && event.candidate_mitre_techniques.length > 0 && (
            <Field label="MITRE Candidates" value={event.candidate_mitre_techniques.join(", ")} />
          )}
        </Section>

        <Section title="Provenance details">
          <Field label="Ingestion ID" value={event.ingestion_id} copyable mono />
          <Field label="Trace ID" value={event.trace_id} copyable mono />
          <Field label="Parser name" value={event.parser_name} />
          <Field label="Parser version" value={event.parser_version} />
          <Field label="Schema version" value={event.schema_version} />
          <Field label="Confidence" value={event.normalization_confidence} />

          {event.normalization_warnings && event.normalization_warnings.length > 0 && (
            <div className="mt-4 rounded bg-amber-950/10 p-3 border border-amber-900/40 font-mono">
              <div className="flex items-center gap-2 text-amber-500 mb-2">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-xs font-bold uppercase">Normalization Warnings</span>
              </div>
              <ul className="list-disc pl-5 text-[11px] text-amber-400/80 space-y-1">
                {event.normalization_warnings.map((w: string, i: number) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}
        </Section>

        {/* Scrollable raw JSON viewer */}
        <Card className="bg-zinc-950 border-zinc-900 shadow-none md:col-span-2">
          <CardHeader className="pb-3 border-b border-zinc-900 flex flex-row items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-xs font-semibold text-zinc-400 uppercase tracking-wider font-mono flex items-center gap-2">
                <FileJson className="h-4 w-4 text-zinc-500" />
                Raw JSON Event Source
              </CardTitle>
              <CardDescription className="text-[10px] text-zinc-500 font-mono">
                Full OpenSearch index payload document
              </CardDescription>
            </div>
            <div className="flex items-center">
              <CopyButton value={JSON.stringify(event, null, 2)} />
            </div>
          </CardHeader>
          <CardContent className="p-4">
            <pre className="text-[11px] text-zinc-400 font-mono overflow-auto max-h-[400px] bg-zinc-950/40 p-4 border border-zinc-900 rounded select-all leading-relaxed whitespace-pre-wrap break-all">
              {JSON.stringify(event, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
