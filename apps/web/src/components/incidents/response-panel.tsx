"use client";

import React, { useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ShieldCheck, Zap, Lock, RefreshCw, CheckCircle2, Play, Check, X } from "lucide-react";
import {
  useCreateResponseRecommendation,
  useDecideResponseApproval,
  useDryRunResponse,
  useRequestResponseApproval,
  useResponseRecommendations,
} from "@/hooks/use-responses";
import { useMe } from "@/hooks/use-me";
import { canExecuteApprovedDryRun } from "@/lib/monitoring";

interface ResponsePanelProps {
  incidentId: string;
}

const PLAYBOOKS = [
  {
    id: "pb-host-isolate",
    action_type: "host_isolation",
    name: "Host Network Isolation",
    description: "Isolates the target host from the internal network while keeping C2 inspection channels open.",
    target: "Host server-01 / 192.168.1.10",
    rationale: "High risk PowerShell execution detected with LSASS memory dump attempt.",
    risk: "LOW - Isolated host maintains SOC management connection.",
  },
  {
    id: "pb-ip-block",
    action_type: "block_ip",
    name: "Edge Firewall IP Block",
    description: "Pushes dynamic drop rule to edge firewalls for suspicious remote source IP.",
    target: "Remote IP 45.91.x.x",
    rationale: "Multiple failed authentication attempts originating from malicious ASN.",
    risk: "LOW - Dynamic rule expires in 24 hours.",
  },
  {
    id: "pb-revoke-creds",
    action_type: "revoke_credentials",
    name: "Revoke Active Kerberos / User Tokens",
    description: "Revokes active Kerberos ticket granting tokens and forces MFA re-authentication.",
    target: "User: admin_user",
    rationale: "Targeted account involved in brute force and credential access anomaly.",
    risk: "MEDIUM - Requires user re-login.",
  },
];

export function ResponsePanel({ incidentId }: ResponsePanelProps) {
  const { data: recommendations, isLoading, refetch, isFetching } = useResponseRecommendations(incidentId);
  const { data: currentUser } = useMe();
  const createMutation = useCreateResponseRecommendation();
  const requestApprovalMutation = useRequestResponseApproval();
  const decideApprovalMutation = useDecideResponseApproval();
  const dryRunMutation = useDryRunResponse();
  const [lastExecution, setLastExecution] = useState<{ status: string; verificationStatus?: string } | null>(null);
  const roles = new Set(currentUser?.roles ?? []);
  const canRecommend = Boolean(currentUser?.is_superuser || roles.has("administrator") || roles.has("soc_analyst"));
  const canApprove = Boolean(currentUser?.is_superuser || roles.has("administrator") || roles.has("security_manager"));
  const canExecute = canApprove;
  const responseError = [
    createMutation.error,
    requestApprovalMutation.error,
    decideApprovalMutation.error,
    dryRunMutation.error,
  ].find((error): error is Error => error instanceof Error);

  const handleTriggerPlaybook = (pb: (typeof PLAYBOOKS)[0]) => {
    createMutation.mutate({
      incidentId,
      action_type: pb.action_type,
      playbook_id: pb.id,
      target_reference: pb.target,
      rationale: pb.rationale,
      impact: pb.risk.startsWith("LOW") ? "low" : "medium",
      reversibility: "reversible",
    });
  };

  const confirmDecision = (recommendationId: string, decision: "approved" | "rejected") => {
    const verb = decision === "approved" ? "approve" : "reject";
    if (window.confirm(`Confirm ${verb} for this response proposal? This decision will be recorded.`)) {
      decideApprovalMutation.mutate({ recommendationId, decision });
    }
  };

  const executeDryRun = (recommendationId: string) => {
    if (!window.confirm("Run a validated dry run? No external containment action will be performed.")) return;
    dryRunMutation.mutate(recommendationId, {
      onSuccess: (execution) => setLastExecution({ status: execution.status, verificationStatus: execution.verification_status }),
    });
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center border-b border-zinc-900 pb-3">
        <div>
          <h3 className="text-lg font-medium text-zinc-100 flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            Response workflow
          </h3>
          <p className="text-xs text-zinc-500 mt-1">
            Create response proposals, request human review, and run validated dry-run simulations.
          </p>
        </div>

        <Button
          onClick={() => refetch()}
          disabled={isFetching}
          variant="outline"
          className="h-8 border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 text-xs px-3"
        >
          <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isFetching ? "animate-spin text-indigo-400" : ""}`} />
          Refresh Responses
        </Button>
      </div>

      <Alert className="bg-emerald-950/20 border-emerald-900/40 text-emerald-400">
        <ShieldCheck className="h-4 w-4 text-emerald-400" />
        <AlertTitle className="text-emerald-300 font-bold uppercase tracking-wider text-xs">
          Human approval required
        </AlertTitle>
        <AlertDescription className="text-[11px] leading-relaxed mt-1 text-emerald-400/80">
          Response proposals are subject to role checks and administrative approval. The available execution mode is a validated dry run; no external containment is initiated from this panel.
        </AlertDescription>
      </Alert>

      {responseError && (
        <Alert className="border-red-900/50 bg-red-950/20 text-red-300">
          <AlertTitle className="text-xs font-bold">Response workflow request failed</AlertTitle>
          <AlertDescription className="mt-1 text-[11px]">{responseError.message}</AlertDescription>
        </Alert>
      )}

      {lastExecution && (
        <Alert className="border-emerald-700/40 bg-emerald-950/20 text-emerald-200" aria-live="polite">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <AlertTitle>Validated only — no external action performed</AlertTitle>
          <AlertDescription className="text-[11px]">Execution status: {lastExecution.status}{lastExecution.verificationStatus ? ` · verification: ${lastExecution.verificationStatus}` : ""}</AlertDescription>
        </Alert>
      )}

      {/* Available Containment Playbooks */}
      <div className="space-y-3">
        <div className="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
          <Zap className="h-4 w-4 text-amber-400" />
          Response proposal templates
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {PLAYBOOKS.map((pb) => (
            <Card key={pb.id} className="bg-zinc-950/40 border-zinc-900 shadow-none flex flex-col justify-between">
              <CardHeader className="p-4 pb-2">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-widest bg-indigo-950/20 border border-indigo-900/40 px-1.5 py-0.5 rounded">
                    {pb.action_type}
                  </span>
                  <span className="text-[9px] text-zinc-650 font-mono">{pb.id}</span>
                </div>
                <CardTitle className="text-xs font-bold text-zinc-200 mt-2 uppercase font-mono">
                  {pb.name}
                </CardTitle>
                <CardDescription className="text-[10px] text-zinc-500 font-mono leading-relaxed mt-1">
                  {pb.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 pt-2 border-t border-zinc-900 mt-3 space-y-3">
                <div className="text-[10px] text-zinc-400">
                  <span className="text-zinc-600 font-semibold uppercase">Target:</span> {pb.target}
                </div>
                <Button
                  onClick={() => handleTriggerPlaybook(pb)}
                  disabled={!canRecommend || createMutation.isPending}
                  title={canRecommend ? undefined : "Your role cannot propose response actions."}
                  className="w-full h-8 bg-emerald-950/40 border border-emerald-900/60 hover:bg-emerald-900/40 text-emerald-400 text-xs font-mono"
                >
                  <Play className="h-3.5 w-3.5 mr-1.5" />
                  Propose Containment
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Recommended Actions Log */}
      <div className="space-y-3 pt-4 border-t border-zinc-900">
        <div className="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
          <Lock className="h-4 w-4 text-indigo-400" />
          Incident response record ({recommendations?.length || 0})
        </div>

        {isLoading ? (
          <div className="py-8 text-center text-zinc-600 text-xs">Loading response logs...</div>
        ) : !recommendations || recommendations.length === 0 ? (
          <div className="border border-dashed border-zinc-900 rounded p-6 text-center text-zinc-650 text-xs">
            No containment recommendations proposed for this incident yet. Click &quot;Propose Containment&quot; above to trigger a playbook.
          </div>
        ) : (
          <div className="space-y-2">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className="flex items-center justify-between p-3 border border-zinc-900 rounded bg-zinc-950/40 text-xs"
              >
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <div>
                    <div className="font-bold text-zinc-200 uppercase">{rec.action_type.replace("_", " ")}</div>
                    <div className="text-[10px] text-zinc-500">Target: {rec.target_reference}</div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-[9px] font-bold uppercase tracking-wider bg-emerald-950/30 border border-emerald-900/50 text-emerald-400 px-2 py-0.5 rounded">
                    {rec.status}
                  </span>
                  <span className="text-[10px] text-zinc-650">By: {rec.created_by || "analyst"}</span>
                </div>
                <div className="flex items-center gap-2">
                  {rec.status === "proposed" && canRecommend && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => requestApprovalMutation.mutate(rec.id)}
                      disabled={requestApprovalMutation.isPending}
                      className="h-7 border-zinc-800 text-[10px]"
                    >
                      Request Review
                    </Button>
                  )}
                  {rec.status === "pending_review" && canApprove && rec.created_by !== currentUser?.username && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => confirmDecision(rec.id, "approved")}
                        disabled={decideApprovalMutation.isPending}
                        className="h-7 bg-emerald-950/40 text-emerald-400 text-[10px]"
                      >
                        <Check className="mr-1 h-3 w-3" /> Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => confirmDecision(rec.id, "rejected")}
                        disabled={decideApprovalMutation.isPending}
                        className="h-7 border-red-900/50 text-red-400 text-[10px]"
                      >
                        <X className="mr-1 h-3 w-3" /> Reject
                      </Button>
                    </>
                  )}
                  {canExecuteApprovedDryRun(rec.status, canExecute) && (
                    <Button
                      size="sm"
                      onClick={() => executeDryRun(rec.id)}
                      disabled={dryRunMutation.isPending}
                      className="h-7 bg-indigo-950/40 text-indigo-300 text-[10px]"
                    >
                      Validated Dry Run
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
