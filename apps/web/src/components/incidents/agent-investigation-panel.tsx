"use client";

import React, { useEffect } from "react";
import { useIncidentAgents, useTriggerIncidentAgent } from "@/hooks/use-incidents";
import { useMe } from "@/hooks/use-me";
import {
  BrainCircuit,
  CheckCircle,
  FileText,
  Loader2,
  ShieldAlert,
  XCircle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface AgentInvestigationPanelProps {
  incidentId: string;
}

export function AgentInvestigationPanel({
  incidentId,
}: AgentInvestigationPanelProps) {
  const { data: executions, isLoading, isError, refetch } = useIncidentAgents(incidentId);
  const triggerAgentMutation = useTriggerIncidentAgent();
  const { data: currentUser } = useMe();

  const execution = executions && executions.length > 0 ? executions[0] : null;

  // Authorization checks
  const isAuthorizedToTrigger =
    currentUser?.is_superuser ||
    currentUser?.roles.includes("admin") ||
    currentUser?.roles.includes("soc_analyst");

  // Refresh while an investigation is running/queued
  useEffect(() => {
    if (
      !execution ||
      (execution.status !== "RUNNING" &&
        execution.status !== "QUEUED")
    ) {
      return;
    }

    const interval = setInterval(() => {
      refetch();
    }, 3000);

    return () => clearInterval(interval);
  }, [execution, refetch]);

  const triggerInvestigation = () => {
    if (triggerAgentMutation.isPending || isRunning) return;
    triggerAgentMutation.mutate({ incidentId, workflowType: "full_investigation" });
  };

  const isRunning =
    execution?.status === "RUNNING" ||
    execution?.status === "QUEUED";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-medium">
            Agentic AI Investigation
          </h3>
          <p className="text-sm text-muted-foreground">
            Autonomous investigation for this incident
          </p>
        </div>

        {isAuthorizedToTrigger && (
          <Button
            onClick={triggerInvestigation}
            disabled={triggerAgentMutation.isPending || isRunning}
          >
            {triggerAgentMutation.isPending || isRunning ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {execution?.status === "QUEUED"
                  ? "Queued..."
                  : "Investigating..."}
              </>
            ) : (
              <>
                <BrainCircuit className="mr-2 h-4 w-4" />
                Start Investigation
              </>
            )}
          </Button>
        )}
      </div>

      {/* Error */}
      {(isError || triggerAgentMutation.isError) && (
        <Alert>
          <XCircle className="h-4 w-4 text-red-500" />
          <AlertTitle>
            Investigation Error
          </AlertTitle>
          <AlertDescription>
            Failed to process agent investigation. Confirm backend API or role settings and try again.
          </AlertDescription>
        </Alert>
      )}

      {/* No investigation yet */}
      {!execution && !isLoading && !isError && (
        <Card className="bg-zinc-950/20 border-zinc-900 shadow-none">
          <CardContent className="py-8 text-center">
            <BrainCircuit className="mx-auto mb-3 h-10 w-10 text-zinc-700" />
            <p className="font-medium text-zinc-400">
              No investigation has been run
            </p>
            <p className="mt-1 text-xs text-zinc-500 max-w-sm mx-auto">
              Start an investigation to let the AI agents analyze this incident's correlated telemetry.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Loading Skeletons */}
      {isLoading && (
        <Card className="bg-zinc-950/20 border-zinc-900 shadow-none">
          <CardContent className="py-6 space-y-4">
            <Loader2 className="h-6 w-6 animate-spin text-zinc-500" />
            <p className="text-xs text-zinc-500 font-mono">Retrieving agent execution logs...</p>
          </CardContent>
        </Card>
      )}

      {/* Investigation data */}
      {execution && (
        <Card className="bg-zinc-950/20 border-zinc-900 shadow-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm text-zinc-300 font-mono uppercase tracking-wider">
              <BrainCircuit className="h-5 w-5 text-indigo-400" />
              Investigation Status
            </CardTitle>
            <CardDescription className="text-xs font-mono">
              Workflow: {execution.workflow_type}
              {execution.requested_by
                ? ` • Requested by ${execution.requested_by}`
                : ""}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* QUEUED */}
            {execution.status === "QUEUED" && (
              <Alert className="bg-indigo-950/10 border-indigo-950 text-indigo-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <AlertTitle>
                  Investigation Queued
                </AlertTitle>
                <AlertDescription className="text-xs">
                  The investigation has been created and is waiting for the AI worker to process it.
                </AlertDescription>
              </Alert>
            )}

            {/* RUNNING */}
            {execution.status === "RUNNING" && (
              <Alert className="bg-indigo-950/10 border-indigo-950 text-indigo-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <AlertTitle>
                  Investigation in Progress
                </AlertTitle>
                <AlertDescription className="text-xs">
                  The AI investigation is currently running. This panel will automatically refresh.
                </AlertDescription>
              </Alert>
            )}

            {/* COMPLETED */}
            {execution.status === "COMPLETED" && (
              <>
                <Alert className="bg-emerald-950/10 border-emerald-950 text-emerald-400">
                  <CheckCircle className="h-4 w-4" />
                  <AlertTitle>
                    Investigation Complete
                  </AlertTitle>
                  <AlertDescription className="text-xs">
                    The AI investigation has completed successfully.
                  </AlertDescription>
                </Alert>

                <div className="grid gap-4 md:grid-cols-2">
                  <Card className="bg-zinc-950 border-zinc-900 shadow-none">
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="flex items-center gap-2 text-xs font-bold text-zinc-400 uppercase tracking-wider font-mono">
                        <ShieldAlert className="h-4 w-4 text-zinc-500" />
                        Investigation Result
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0 text-xs text-zinc-500 font-mono leading-relaxed">
                      Investigation execution completed. Detailed risk assessment will appear here when the agent worker stores its results.
                    </CardContent>
                  </Card>

                  <Card className="bg-zinc-950 border-zinc-900 shadow-none">
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="flex items-center gap-2 text-xs font-bold text-zinc-400 uppercase tracking-wider font-mono">
                        <FileText className="h-4 w-4 text-zinc-500" />
                        Recommendations
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0 text-xs text-zinc-500 font-mono leading-relaxed">
                      Agent recommendations will appear here once the investigation workflow produces its final response.
                    </CardContent>
                  </Card>
                </div>
              </>
            )}

            {/* FAILED */}
            {execution.status === "FAILED" && (
              <Alert className="bg-red-950/10 border-red-950 text-red-400">
                <XCircle className="h-4 w-4" />
                <AlertTitle>
                  Investigation Failed
                </AlertTitle>
                <AlertDescription className="text-xs">
                  The AI investigation failed to complete. Check the agent worker logs for details.
                </AlertDescription>
              </Alert>
            )}

            {/* CANCELLED */}
            {execution.status === "CANCELLED" && (
              <Alert className="bg-zinc-950 border-zinc-900 text-zinc-400">
                <XCircle className="h-4 w-4" />
                <AlertTitle>
                  Investigation Cancelled
                </AlertTitle>
                <AlertDescription className="text-xs">
                  This investigation was cancelled.
                </AlertDescription>
              </Alert>
            )}

            {/* Unknown status */}
            {![
              "QUEUED",
              "RUNNING",
              "COMPLETED",
              "FAILED",
              "CANCELLED",
            ].includes(execution.status) && (
              <Alert>
                <AlertTitle>
                  Status: {execution.status}
                </AlertTitle>
                <AlertDescription className="text-xs">
                  The investigation returned an unknown status.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}