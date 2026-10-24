"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  useIncident,
  useUpdateIncidentStatus,
  useIncidentNotes,
  useAddIncidentNote,
} from "@/hooks/use-incidents";
import { useMe } from "@/hooks/use-me";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SeverityBadge, StatusIndicator } from "@/components/ui/soc-indicators";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCorrelationPanel } from "@/components/incidents/alert-correlation-panel";
import { PredictionPanel } from "@/components/incidents/prediction-panel";
import { AgentInvestigationPanel } from "@/components/incidents/agent-investigation-panel";
import { ResponsePanel } from "@/components/incidents/response-panel";
import { ArrowLeft, AlertCircle, RefreshCw, Send, ShieldAlert, Clock, User, MessageSquare } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from "date-fns";

const ALLOWED_TRANSITIONS: Record<string, string[]> = {
  new: ["triaged", "false_positive", "closed"],
  triaged: ["investigating", "false_positive", "closed"],
  investigating: ["awaiting_approval", "contained", "resolved"],
  awaiting_approval: ["contained", "resolved", "investigating"],
  contained: ["resolved"],
  resolved: ["closed"],
  false_positive: ["new"],
  closed: ["new", "investigating"],
};

export default function IncidentDetailPage() {
  const { incidentId } = useParams() as { incidentId: string };
  const router = useRouter();

  const { data: incident, isLoading, isError, refetch } = useIncident(incidentId);
  const { data: currentUser } = useMe();
  const updateStatusMutation = useUpdateIncidentStatus();

  // Analyst Notes
  const { data: notes, isLoading: isLoadingNotes } = useIncidentNotes(incidentId);
  const addNoteMutation = useAddIncidentNote();
  const [newNoteText, setNewNoteText] = useState("");

  // Status transitions state
  const [pendingStatus, setPendingStatus] = useState<string | null>(null);
  const [transitionReason, setTransitionReason] = useState("");

  // Role authorization checks
  const isAuthorizedToEdit =
    currentUser?.is_superuser ||
    currentUser?.roles.includes("admin") ||
    currentUser?.roles.includes("soc_analyst");

  const handleStatusSelect = (targetStatus: string) => {
    if (targetStatus === "false_positive" || targetStatus === "closed") {
      // Require reason before mutating
      setPendingStatus(targetStatus);
      setTransitionReason("");
    } else {
      updateStatusMutation.mutate({ incidentId, status: targetStatus });
    }
  };

  const handleConfirmTransition = () => {
    if (!pendingStatus) return;
    updateStatusMutation.mutate(
      {
        incidentId,
        status: pendingStatus,
        reason: transitionReason.trim() || undefined,
      },
      {
        onSuccess: () => {
          setPendingStatus(null);
          setTransitionReason("");
        },
      }
    );
  };

  const handleAddNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteText.trim() || addNoteMutation.isPending) return;
    addNoteMutation.mutate(
      { incidentId, content: newNoteText.trim() },
      {
        onSuccess: () => {
          setNewNoteText("");
        },
      }
    );
  };

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

        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-20 bg-zinc-900 rounded-lg" />
          ))}
        </div>

        <div className="h-80 bg-zinc-900 rounded-lg" />
      </div>
    );
  }

  // 2. Error State
  if (isError || !incident) {
    return (
      <div className="flex h-[400px] flex-col items-center justify-center rounded-lg border border-red-900/40 bg-red-950/10 p-6 text-center font-mono">
        <AlertCircle className="mb-4 h-12 w-12 text-red-500" />
        <h3 className="text-lg font-bold text-red-400">Incident not found</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-2 mb-6">
          The requested incident workspace could not be loaded from the backend API.
        </p>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => router.push("/incidents")}
            variant="outline"
            className="border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-xs"
          >
            Back to Incidents
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

  const allowedOptions = ALLOWED_TRANSITIONS[incident.status.toLowerCase()] || [];

  return (
    <div className="space-y-6 font-mono">
      {/* Header Block */}
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between border-b border-zinc-900 pb-4">
        <div className="space-y-2">
          <button
            onClick={() => router.push("/incidents")}
            className="inline-flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Incidents
          </button>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">{incident.title}</h2>
          <p className="text-xs text-zinc-500">ID: {incident.id}</p>
        </div>

        {/* Workflow State Transition Select */}
        <div className="flex flex-col items-end gap-1.5">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Incident State</span>
          {isAuthorizedToEdit ? (
            <div className="flex flex-col items-end gap-2">
              <div className="flex items-center gap-2">
                <Select
                  value={incident.status}
                  onValueChange={(val) => val && handleStatusSelect(val)}
                  disabled={updateStatusMutation.isPending || !!pendingStatus}
                >
                  <SelectTrigger className="w-[180px] h-8 bg-zinc-950 border-zinc-900 text-xs capitalize">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-950 border-zinc-900 text-xs">
                    <SelectItem value={incident.status}>{incident.status.replace("_", " ")}</SelectItem>
                    {allowedOptions.map((opt) => (
                      <SelectItem key={opt} value={opt} className="capitalize">
                        {opt.replace("_", " ")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {updateStatusMutation.isPending && (
                  <span className="text-[10px] text-indigo-400 animate-pulse">Saving...</span>
                )}
              </div>

              {/* Transition reason input overlay */}
              {pendingStatus && (
                <div className="mt-2 p-3 border border-zinc-800 bg-zinc-950 rounded space-y-2 w-72 text-left z-10">
                  <p className="text-[10px] text-zinc-400">
                    Provide reason for transitioning to <span className="text-amber-500 font-bold uppercase">{pendingStatus}</span>:
                  </p>
                  <Input
                    placeholder="Describe reason..."
                    value={transitionReason}
                    onChange={(e) => setTransitionReason(e.target.value)}
                    className="h-7 bg-zinc-900 border-zinc-800 text-xs font-mono"
                  />
                  <div className="flex justify-end gap-2 pt-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setPendingStatus(null)}
                      className="h-6 text-[10px] px-2"
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleConfirmTransition}
                      disabled={updateStatusMutation.isPending}
                      className="h-6 text-[10px] px-2 bg-indigo-600 hover:bg-indigo-700 text-zinc-100"
                    >
                      Confirm
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="px-3 py-1.5 border border-zinc-900 bg-zinc-950/40 rounded">
              <StatusIndicator status={incident.status} />
            </div>
          )}
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Severity</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <SeverityBadge severity={incident.severity} className="text-sm px-2.5 py-1" />
          </CardContent>
        </Card>

        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Status State</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <StatusIndicator status={incident.status} className="text-sm font-semibold" />
          </CardContent>
        </Card>

        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Risk Index</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xl font-bold font-mono">
              <span className={incident.risk_score >= 80 ? "text-red-500" : incident.risk_score >= 50 ? "text-amber-500" : "text-zinc-400"}>
                {incident.risk_score.toFixed(1)}
              </span>
              <span className="text-xs text-zinc-600 font-normal"> / 100</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Correlated Alerts</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xl font-bold font-mono text-zinc-300">
              {incident.alert_count}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs Panel Workspace */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="bg-zinc-950 border border-zinc-900 p-1 flex overflow-x-auto h-auto max-w-full justify-start rounded-lg">
          <TabsTrigger value="overview" className="text-xs font-mono py-1.5 px-3">Overview</TabsTrigger>
          <TabsTrigger value="agents" className="text-xs font-mono py-1.5 px-3">AI Agent Investigation</TabsTrigger>
          <TabsTrigger value="alerts" className="text-xs font-mono py-1.5 px-3">Correlated Alerts</TabsTrigger>
          <TabsTrigger value="prediction" className="text-xs font-mono py-1.5 px-3">Attack Progression</TabsTrigger>
          <TabsTrigger value="notes" className="text-xs font-mono py-1.5 px-3">Analyst Notes</TabsTrigger>
          <TabsTrigger value="responses" className="text-xs font-mono py-1.5 px-3">Response Actions</TabsTrigger>
        </TabsList>

        {/* Tab 1: Overview */}
        <TabsContent value="overview">
          <div className="grid gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2 bg-zinc-950 border-zinc-900 shadow-none">
              <CardHeader>
                <CardTitle className="text-xs font-semibold text-zinc-500 uppercase font-mono">Incident Summary Description</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-xs text-zinc-300 leading-relaxed bg-zinc-950/40 p-4 border border-zinc-900 rounded">
                  {incident.description || "No analytical description provided for this incident."}
                </p>

                {incident.resolution_summary && (
                  <div className="space-y-1">
                    <h4 className="text-[10px] text-zinc-500 uppercase font-bold">Resolution Summary</h4>
                    <p className="text-xs text-emerald-400 bg-zinc-950/60 p-3 border border-zinc-900 rounded">
                      {incident.resolution_summary}
                    </p>
                  </div>
                )}

                {incident.closure_reason && (
                  <div className="space-y-1">
                    <h4 className="text-[10px] text-zinc-500 uppercase font-bold">Closure Reason</h4>
                    <p className="text-xs text-zinc-400 bg-zinc-950/60 p-3 border border-zinc-900 rounded">
                      {incident.closure_reason}
                    </p>
                  </div>
                )}

                {incident.false_positive_reason && (
                  <div className="space-y-1">
                    <h4 className="text-[10px] text-zinc-500 uppercase font-bold">False Positive Reason</h4>
                    <p className="text-xs text-amber-500 bg-zinc-950/60 p-3 border border-zinc-900 rounded">
                      {incident.false_positive_reason}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-zinc-950 border-zinc-900 shadow-none">
              <CardHeader>
                <CardTitle className="text-xs font-semibold text-zinc-500 uppercase font-mono">Telemetry Context</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-xs">
                <div className="space-y-2 border-b border-zinc-900 pb-3">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">First Detected:</span>
                    <span className="text-zinc-300">{incident.first_seen ? new Date(incident.first_seen).toLocaleString() : "N/A"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Last Active:</span>
                    <span className="text-zinc-300">{incident.last_seen ? new Date(incident.last_seen).toLocaleString() : "N/A"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Events Count:</span>
                    <span className="text-zinc-300 font-bold">{incident.event_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Assignee ID:</span>
                    <span className="text-zinc-300">{incident.assignee_id || "Unassigned"}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="text-[10px] font-bold text-zinc-500 uppercase">Tags</h4>
                  {incident.tags && incident.tags.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {incident.tags.map((t, i) => (
                        <Badge key={i} variant="outline" className="bg-zinc-950 border-zinc-800 text-[10px] text-zinc-400">
                          {t}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[10px] text-zinc-600 italic">No tags associated.</p>
                  )}
                </div>

                <div className="space-y-2 border-t border-zinc-900 pt-3">
                  <h4 className="text-[10px] font-bold text-zinc-500 uppercase">MITRE Ref Candidate</h4>
                  {incident.candidate_mitre_references && incident.candidate_mitre_references.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {incident.candidate_mitre_references.map((ref, i) => (
                        <Badge key={i} className="bg-indigo-950/20 border border-indigo-900/40 text-indigo-400 text-[10px]">
                          {ref}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[10px] text-zinc-600 italic">No MITRE mappings flagged.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab 2: AI Agent Investigation */}
        <TabsContent value="agents">
          <Card className="bg-zinc-950 border-zinc-900 shadow-none">
            <CardContent className="pt-6">
              <AgentInvestigationPanel incidentId={incidentId} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Correlated Alerts */}
        <TabsContent value="alerts">
          <Card className="bg-zinc-950 border-zinc-900 shadow-none">
            <CardContent className="pt-6">
              <AlertCorrelationPanel incidentId={incidentId} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 4: Attack Prediction */}
        <TabsContent value="prediction">
          <PredictionPanel incidentId={incidentId} />
        </TabsContent>

        {/* Tab 5: Analyst Notes */}
        <TabsContent value="notes" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Timeline Area */}
            <Card className="lg:col-span-2 bg-zinc-950 border-zinc-900 shadow-none">
              <CardHeader>
                <CardTitle className="text-xs font-semibold text-zinc-500 uppercase font-mono flex items-center gap-1.5">
                  <MessageSquare className="h-4 w-4 text-zinc-500" />
                  Notes Activity Feed
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6 max-h-[450px] overflow-y-auto">
                {isLoadingNotes ? (
                  <div className="space-y-3">
                    <Skeleton className="h-12 bg-zinc-900 w-full" />
                    <Skeleton className="h-12 bg-zinc-900 w-full" />
                  </div>
                ) : !notes || notes.length === 0 ? (
                  <div className="text-center py-10 border border-dashed border-zinc-900 rounded">
                    <p className="text-xs text-zinc-500 italic">No analyst notes recorded yet.</p>
                  </div>
                ) : (
                  <div className="relative border-l border-zinc-900 pl-4 space-y-6 ml-2">
                    {notes.map((note) => (
                      <div key={note.id} className="relative space-y-1">
                        {/* Bullet node */}
                        <div className="absolute -left-[21px] top-1 h-3.5 w-3.5 rounded-full border border-zinc-900 bg-zinc-950 flex items-center justify-center">
                          <div className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
                        </div>

                        <div className="flex items-center gap-2 text-[10px] text-zinc-500">
                          <span className="font-semibold text-zinc-400 flex items-center gap-1">
                            <User className="h-3 w-3 text-zinc-500" />
                            {note.author_id}
                          </span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3 text-zinc-500" />
                            {formatDistanceToNow(new Date(note.created_at), { addSuffix: true })}
                          </span>
                        </div>
                        <p className="text-xs text-zinc-300 bg-zinc-900/20 border border-zinc-950 p-3 rounded leading-relaxed">
                          {note.content}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Note input overlay */}
            <Card className="bg-zinc-950 border-zinc-900 shadow-none h-fit">
              <CardHeader>
                <CardTitle className="text-xs font-semibold text-zinc-500 uppercase font-mono">Record Finding</CardTitle>
                <CardDescription className="text-[11px] text-zinc-500">
                  Append persistent log comments to this incident.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAddNote} className="space-y-3">
                  <textarea
                    placeholder="Enter technical details, findings, or containment logs..."
                    value={newNoteText}
                    onChange={(e) => setNewNoteText(e.target.value)}
                    rows={4}
                    className="w-full text-xs font-mono bg-zinc-900 border border-zinc-800 rounded p-2.5 text-zinc-300 focus:outline-none focus:border-zinc-700 placeholder:text-zinc-600 resize-none"
                  />
                  <Button
                    type="submit"
                    disabled={!newNoteText.trim() || addNoteMutation.isPending}
                    className="w-full text-xs bg-indigo-650 hover:bg-indigo-700 text-zinc-100 flex items-center justify-center gap-1.5"
                  >
                    <Send className="h-3.5 w-3.5" />
                    Publish Note
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab 6: Response Actions */}
        <TabsContent value="responses">
          <Card className="bg-zinc-950 border-zinc-900 shadow-none">
            <CardContent className="pt-6">
              <ResponsePanel incidentId={incidentId} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
