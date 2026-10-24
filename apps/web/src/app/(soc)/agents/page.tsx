"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  BrainCircuit,
  Cpu,
  Search,
  RefreshCw,
  Loader2,
  AlertCircle,
  XCircle,
  Clock,
  User,
  Activity,
  CheckCircle2,
  FileText,
  X,
  ChevronRight,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react";
import { useIncidentAgents, useIncidents, IncidentResponse } from "@/hooks/use-incidents";
import { useAgentExecution, useCancelAgentExecution } from "@/hooks/use-agents";
import { useMe } from "@/hooks/use-me";
import { formatDistanceToNow } from "date-fns";

// Static agent definitions corresponding to the system configuration
const SYSTEM_AGENTS = [
  {
    name: "Verification Specialist",
    type: "validation",
    description: "Heuristically validates incoming threat vectors against normalized system categories.",
    version: "v2.1",
    model: "gemini-2.0-flash",
    capabilities: ["telemetry match", "false positive parsing"],
  },
  {
    name: "Incident Investigator",
    type: "forensics",
    description: "Constructs chronological progression paths by matching file activities, PIDs, and process lists.",
    version: "v1.8",
    model: "gemini-2.0-pro",
    capabilities: ["process tracking", "command line evaluation"],
  },
  {
    name: "Threat Intel Enricher",
    type: "intelligence",
    description: "Maps telemetry coordinates to geolocations, remote ASN databases, and public reputation indexes.",
    version: "v3.0",
    model: "gemini-2.0-flash",
    capabilities: ["geo tracking", "reputation querying"],
  },
  {
    name: "Risk Assessor",
    type: "analyst",
    description: "Evaluates threat criticality, assets criticality, and maps behaviors to MITRE ATT&CK technique IDs.",
    version: "v2.5",
    model: "gemini-2.0-pro",
    capabilities: ["mitre mapping", "impact calculation"],
  },
];

export default function AgentsPage() {
  const { data: currentUser } = useMe();
  const { data: recentIncidents } = useIncidents(0, 5);
  const [incidentSearchId, setIncidentSearchId] = useState<string>("");
  const [activeIncidentId, setActiveIncidentId] = useState<string>("");
  const [selectedExecutionId, setSelectedExecutionId] = useState<string | null>(null);

  // Fetch executions if an incident ID is active
  const {
    data: executions,
    isLoading: isExecutionsLoading,
    isError: isExecutionsError,
    refetch: refetchExecutions,
    isFetching: isExecutionsFetching,
  } = useIncidentAgents(activeIncidentId);

  // Authorize managers/administrators to cancel executions
  const isAuthorizedToCancel = !!(
    currentUser?.is_superuser ||
    currentUser?.roles?.includes("admin") ||
    currentUser?.roles?.includes("soc_analyst")
  );

  const [searchValidationError, setSearchValidationError] = useState<string | null>(null);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleaned = incidentSearchId.trim();
    const isValidUuid = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(cleaned);

    if (!isValidUuid) {
      setSearchValidationError("Please enter a valid 36-character Incident UUID (e.g. d0f1b7a3-ce57-429a-b2de-c9145dfd0272).");
      return;
    }

    setSearchValidationError(null);
    setActiveIncidentId(cleaned);
  };

  return (
    <div className="space-y-6 font-mono pb-12">
      {/* Header Block */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">AI Agents</h2>
          <p className="text-xs text-zinc-500 mt-1">
            LangGraph-Powered Autonomous Threat Hunters & Analysts
          </p>
        </div>
      </div>

      {/* Agents Profiles Section */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {SYSTEM_AGENTS.map((agent) => (
          <Card key={agent.name} className="bg-zinc-950 border-zinc-900 shadow-none flex flex-col justify-between">
            <CardHeader className="p-4 pb-2">
              <div className="flex items-center justify-between">
                <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-widest bg-indigo-950/20 border border-indigo-900/40 px-1.5 py-0.5 rounded">
                  {agent.type}
                </span>
                <span className="text-[9px] text-zinc-650 font-mono">{agent.version}</span>
              </div>
              <CardTitle className="text-xs font-bold text-zinc-200 mt-3 flex items-center gap-1.5 uppercase font-mono">
                <Cpu className="h-3.5 w-3.5 text-indigo-400" />
                {agent.name}
              </CardTitle>
              <CardDescription className="text-[10px] text-zinc-500 leading-relaxed font-mono mt-1">
                {agent.description}
              </CardDescription>
            </CardHeader>
            <CardContent className="p-4 pt-0 border-t border-zinc-900 mt-4 flex flex-col gap-1.5">
              <div className="text-[9px] text-zinc-600 font-bold uppercase tracking-wider font-mono">
                Core Capabilities:
              </div>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.map((c) => (
                  <span
                    key={c}
                    className="text-[9px] text-zinc-400 bg-zinc-900 border border-zinc-900 px-1 py-0.5 rounded font-mono"
                  >
                    {c}
                  </span>
                ))}
              </div>
              <div className="text-[9px] text-zinc-750 font-mono mt-2 uppercase">
                Model: {agent.model}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Run Execution Log Search Filter */}
      <Card className="bg-zinc-950 border-zinc-900 shadow-none">
        <CardHeader className="p-4 border-b border-zinc-900">
          <CardTitle className="text-xs font-bold text-zinc-400 uppercase tracking-wider font-mono flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-400" />
            AI Execution Logs & History
          </CardTitle>
          <CardDescription className="text-[10px] text-zinc-650 font-mono">
            Query historical LangGraph execution trace logs by providing an Incident ID.
          </CardDescription>
        </CardHeader>

        <CardContent className="p-4 space-y-6">
          {/* Quick Incident Selector Bar */}
          {recentIncidents && recentIncidents.length > 0 && (
            <div className="space-y-2">
              <div className="text-[10px] text-zinc-500 uppercase font-semibold">
                Quick Select Recent Incident:
              </div>
              <div className="flex flex-wrap gap-2">
                {recentIncidents.map((inc: IncidentResponse) => (
                  <button
                    key={inc.id}
                    onClick={() => {
                      setIncidentSearchId(inc.id);
                      setSearchValidationError(null);
                      setActiveIncidentId(inc.id);
                    }}
                    className={`text-[10px] px-2.5 py-1 rounded border font-mono transition-colors ${
                      activeIncidentId === inc.id
                        ? "bg-indigo-950/40 border-indigo-500 text-indigo-300 font-bold"
                        : "bg-zinc-950 border-zinc-900 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
                    }`}
                  >
                    {inc.title} <span className="text-[9px] text-zinc-600">({inc.id.slice(0, 8)}...)</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSearchSubmit} className="flex gap-3 max-w-md">
            <Input
              placeholder="Enter Incident UUID..."
              value={incidentSearchId}
              onChange={(e) => {
                setIncidentSearchId(e.target.value);
                if (searchValidationError) setSearchValidationError(null);
              }}
              className="h-8 bg-zinc-950 border-zinc-900 text-xs font-mono focus:border-zinc-800"
            />
            <Button
              type="submit"
              disabled={!incidentSearchId.trim()}
              className="h-8 bg-indigo-650 hover:bg-indigo-700 text-zinc-100 text-xs px-3 font-mono"
            >
              <Search className="h-3.5 w-3.5 mr-1.5" />
              Search Runs
            </Button>
          </form>

          {searchValidationError && (
            <div className="text-[11px] text-amber-400 font-mono bg-amber-950/20 border border-amber-900/40 p-2.5 rounded max-w-md">
              {searchValidationError}
            </div>
          )}

          {activeIncidentId && (
            <div className="space-y-4 pt-2">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-2">
                <div className="text-xs text-zinc-400">
                  Runs registered to Incident:{" "}
                  <span className="font-bold text-indigo-400">{activeIncidentId}</span>
                </div>
                <Button
                  onClick={() => refetchExecutions()}
                  disabled={isExecutionsFetching}
                  variant="ghost"
                  className="h-7 hover:bg-zinc-900 text-zinc-500 hover:text-zinc-300 text-xs px-2"
                >
                  <RefreshCw
                    className={`h-3 w-3 mr-1.5 ${isExecutionsFetching ? "animate-spin text-indigo-400" : ""}`}
                  />
                  Refresh
                </Button>
              </div>

              {/* Loader */}
              {isExecutionsLoading && (
                <div className="py-8 text-center text-zinc-500">
                  <Loader2 className="mx-auto h-6 w-6 animate-spin mb-2" />
                  <span className="text-xs font-mono">Loading execution logs...</span>
                </div>
              )}

              {/* Error */}
              {isExecutionsError && (
                <div className="rounded border border-red-900/40 bg-red-950/10 p-4 text-center text-red-500 text-xs">
                  <AlertCircle className="mx-auto h-6 w-6 mb-2" />
                  Failed to retrieve logs for this incident. Ensure UUID format is valid.
                </div>
              )}

              {/* Table */}
              {executions && (
                <div className="border border-zinc-900 rounded overflow-hidden">
                  <Table>
                    <TableHeader className="bg-zinc-950/60">
                      <TableRow className="hover:bg-transparent border-zinc-900">
                        <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-44">Run ID</TableHead>
                        <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-44">Workflow</TableHead>
                        <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-28">Status</TableHead>
                        <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-24">Tool Calls</TableHead>
                        <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-24">Duration</TableHead>
                        <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-32">Requested By</TableHead>
                        <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-20 text-right">Details</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {executions.length === 0 ? (
                        <TableRow className="hover:bg-transparent border-none">
                          <TableCell colSpan={7} className="text-center py-12 text-zinc-650 text-xs">
                            No agent execution runs recorded for this incident.
                          </TableCell>
                        </TableRow>
                      ) : (
                        executions.map((exe) => (
                          <TableRow key={exe.id} className="hover:bg-zinc-900/20 border-zinc-900">
                            <TableCell className="font-mono text-zinc-400 text-[11px] py-2 max-w-[120px] truncate">
                              {exe.id}
                            </TableCell>
                            <TableCell className="font-mono text-zinc-200 text-[11px] py-2 capitalize">
                              {exe.workflow_type.replace("_", " ")}
                            </TableCell>
                            <TableCell className="py-2">
                              <span
                                className={`inline-flex items-center rounded px-1.5 py-0.5 text-[9px] font-bold font-mono border uppercase ${
                                  exe.status === "completed"
                                    ? "bg-emerald-950/20 border-emerald-900/40 text-emerald-400"
                                    : exe.status === "running"
                                    ? "bg-indigo-950/20 border-indigo-900/40 text-indigo-400 animate-pulse"
                                    : exe.status === "queued"
                                    ? "bg-zinc-950 border-zinc-900 text-zinc-400"
                                    : "bg-red-950/20 border-red-900/40 text-red-400"
                                }`}
                              >
                                {exe.status}
                              </span>
                            </TableCell>
                            <TableCell className="font-mono text-zinc-400 text-[11px] py-2">
                              {exe.tool_calls_count} calls
                            </TableCell>
                            <TableCell className="font-mono text-zinc-400 text-[11px] py-2">
                              {exe.duration_seconds ? `${exe.duration_seconds}s` : "-"}
                            </TableCell>
                            <TableCell className="font-mono text-zinc-500 text-[11px] py-2 truncate max-w-[100px]">
                              {exe.requested_by || "system"}
                            </TableCell>
                            <TableCell className="py-2 text-right">
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => setSelectedExecutionId(exe.id)}
                                className="h-6 w-6 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-900"
                              >
                                <ChevronRight className="h-4 w-4" />
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          )}

          {!activeIncidentId && (
            <div className="border border-dashed border-zinc-900 rounded p-8 text-center text-zinc-650 text-xs">
              Provide an active Incident ID to trace autonomous agent actions and results.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Execution Details Dialog Modal */}
      {selectedExecutionId && (
        <ExecutionDetailsDialog
          executionId={selectedExecutionId}
          open={!!selectedExecutionId}
          onOpenChange={(open) => !open && setSelectedExecutionId(null)}
          isAuthorizedToCancel={isAuthorizedToCancel}
          refetchList={refetchExecutions}
        />
      )}
    </div>
  );
}

// Subcomponent: Execution Inspector Dialog
interface ExecutionDetailsDialogProps {
  executionId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isAuthorizedToCancel: boolean;
  refetchList: () => void;
}

function ExecutionDetailsDialog({
  executionId,
  open,
  onOpenChange,
  isAuthorizedToCancel,
  refetchList,
}: ExecutionDetailsDialogProps) {
  const { data: exe, isLoading, isError, refetch } = useAgentExecution(executionId);
  const cancelMutation = useCancelAgentExecution();

  const handleCancelRun = () => {
    cancelMutation.mutate(executionId, {
      onSuccess: () => {
        refetch();
        refetchList();
      },
    });
  };

  const isCancelPending = cancelMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-zinc-950 border-zinc-900 text-zinc-100 max-w-3xl max-h-[85vh] overflow-y-auto font-mono text-xs">
        <DialogHeader className="border-b border-zinc-900 pb-3 flex flex-row items-start justify-between">
          <div className="space-y-1">
            <DialogTitle className="text-sm font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <BrainCircuit className="h-4 w-4 text-indigo-400" />
              Execution Trace Inspector
            </DialogTitle>
            <DialogDescription className="text-[10px] text-zinc-500 font-mono">
              ID: {executionId}
            </DialogDescription>
          </div>
        </DialogHeader>

        {isLoading && (
          <div className="py-12 text-center text-zinc-500">
            <Loader2 className="mx-auto h-6 w-6 animate-spin mb-2" />
            Loading execution data...
          </div>
        )}

        {isError && (
          <div className="py-8 text-center text-red-500">
            <AlertCircle className="mx-auto h-6 w-6 mb-2" />
            Unable to fetch execution trace. Ensure connection is stable.
          </div>
        )}

        {exe && (
          <div className="space-y-6 pt-4">
            {/* Metadata Rows */}
            <div className="grid gap-3 grid-cols-2 md:grid-cols-4 bg-zinc-950/40 p-3 border border-zinc-900 rounded">
              <div>
                <div className="text-[9px] text-zinc-650 uppercase font-semibold">Status</div>
                <span
                  className={`inline-flex items-center rounded mt-1 px-1.5 py-0.25 text-[9px] font-bold border uppercase ${
                    exe.status === "completed"
                      ? "bg-emerald-950/20 border-emerald-900/40 text-emerald-400"
                      : exe.status === "running"
                      ? "bg-indigo-950/20 border-indigo-900/40 text-indigo-400"
                      : exe.status === "queued"
                      ? "bg-zinc-950 border-zinc-900 text-zinc-400"
                      : "bg-red-950/20 border-red-900/40 text-red-400"
                  }`}
                >
                  {exe.status}
                </span>
              </div>
              <div>
                <div className="text-[9px] text-zinc-650 uppercase font-semibold">Model Used</div>
                <div className="text-[11px] text-zinc-300 mt-1 truncate">
                  {exe.model_name || "-"} ({exe.model_provider || "-"})
                </div>
              </div>
              <div>
                <div className="text-[9px] text-zinc-650 uppercase font-semibold">Total Steps</div>
                <div className="text-[11px] text-zinc-300 mt-1 font-bold">
                  {exe.steps_completed} completed
                </div>
              </div>
              <div>
                <div className="text-[9px] text-zinc-650 uppercase font-semibold">Elapsed Duration</div>
                <div className="text-[11px] text-zinc-300 mt-1">
                  {exe.duration_seconds ? `${exe.duration_seconds}s` : "-"}
                </div>
              </div>
            </div>

            {/* Error Message if failed */}
            {exe.failure_reason && (
              <div className="p-3 bg-red-950/15 border border-red-900/40 rounded text-red-400 flex items-start gap-2.5">
                <XCircle className="h-4 w-4 shrink-0 text-red-500 mt-0.5" />
                <div>
                  <div className="font-bold text-[10px] uppercase">Failure Reason</div>
                  <div className="text-[11px] mt-0.5 leading-relaxed text-red-300/80">{exe.failure_reason}</div>
                </div>
              </div>
            )}

            {/* Findings Tab / Results blocks */}
            <div className="space-y-4">
              <div className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider border-b border-zinc-900 pb-1 flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5" />
                LangGraph Analysis Findings
              </div>

              {exe.result_data ? (
                <div className="space-y-4">
                  {/* Iterate over result sections if they have values */}
                  {Object.entries(exe.result_data).map(([sectionKey, sectionVal]: [string, any]) => {
                    // Check if it's a section object containing findings
                    if (
                      sectionVal &&
                      typeof sectionVal === "object" &&
                      (Array.isArray(sectionVal.findings) || Array.isArray(sectionVal.recommendations))
                    ) {
                      const findings = sectionVal.findings || [];
                      const recommendations = sectionVal.recommendations || [];
                      const evidence = sectionVal.evidence_references || [];

                      if (findings.length === 0 && recommendations.length === 0) return null;

                      return (
                        <div key={sectionKey} className="border border-zinc-900 bg-zinc-950/30 rounded p-4 space-y-3">
                          <div className="flex items-center justify-between border-b border-zinc-900 pb-2">
                            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">
                              {sectionKey.replace("_", " ")}
                            </span>
                            <span className="text-[9px] text-zinc-500 font-mono capitalize">
                              Confidence: <span className="font-bold text-zinc-400">{sectionVal.confidence || "unknown"}</span>
                            </span>
                          </div>

                          {findings.length > 0 && (
                            <div className="space-y-1">
                              <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-semibold">Key Findings:</div>
                              <ul className="list-disc pl-5 text-[11px] text-zinc-300 space-y-1">
                                {findings.map((f: string, idx: number) => (
                                  <li key={idx} className="leading-relaxed">{f}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {recommendations.length > 0 && (
                            <div className="space-y-1 pt-1.5">
                              <div className="text-[9px] text-zinc-500 uppercase tracking-wider font-semibold">Actions / Recommendations:</div>
                              <ul className="list-disc pl-5 text-[11px] text-zinc-400 space-y-1">
                                {recommendations.map((r: string, idx: number) => (
                                  <li key={idx} className="leading-relaxed">{r}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              ) : (
                <div className="border border-zinc-900 border-dashed rounded p-6 text-center text-zinc-650">
                  {exe.status === "completed"
                    ? "Investigation finished, but no findings output sections were recorded."
                    : "LangGraph findings will appear here once the execution completes."}
                </div>
              )}
            </div>

            {/* In-Depth System Info Block */}
            <div className="space-y-2 border border-zinc-900 p-3 rounded bg-zinc-950/10">
              <div className="text-[9px] text-zinc-600 uppercase tracking-wider font-bold">Metadata Details</div>
              <div className="grid gap-2 grid-cols-2 text-[10px] text-zinc-500">
                <div>Trace ID: <span className="font-mono text-zinc-400 break-all">{exe.trace_id || "-"}</span></div>
                <div>Prompt Version: <span className="font-mono text-zinc-400">{exe.prompt_version || "-"}</span></div>
                <div>Triggered: <span className="font-mono text-zinc-400">{exe.created_at ? new Date(exe.created_at).toLocaleString() : "-"}</span></div>
                <div>Requested By: <span className="font-mono text-zinc-400">{exe.requested_by || "system"}</span></div>
              </div>
            </div>

            {/* Cancel Action Controls */}
            {isAuthorizedToCancel && (exe.status === "running" || exe.status === "queued") && (
              <div className="flex items-center justify-between border-t border-red-950/20 pt-4 mt-2">
                <span className="text-[10px] text-red-500/80 font-mono">
                  This execution can be cancelled safely.
                </span>
                <Button
                  onClick={handleCancelRun}
                  disabled={isCancelPending}
                  variant="destructive"
                  className="h-8 bg-red-950/20 border border-red-900/40 text-red-400 hover:bg-red-900/30 text-xs font-mono"
                >
                  {isCancelPending ? (
                    <>
                      <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                      Cancelling...
                    </>
                  ) : (
                    <>
                      <X className="mr-1.5 h-3.5 w-3.5" />
                      Cancel Execution
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>
        )}

        <DialogFooter className="border-t border-zinc-900 pt-3">
          <Button
            type="button"
            variant="ghost"
            onClick={() => onOpenChange(false)}
            className="h-8 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
