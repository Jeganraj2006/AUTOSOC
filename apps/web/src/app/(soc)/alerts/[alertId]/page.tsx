"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAlert, useUpdateAlertStatus } from "@/hooks/use-alerts";
import { useMe } from "@/hooks/use-me";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { SeverityBadge, StatusIndicator } from "@/components/ui/soc-indicators";
import { ArrowLeft } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { canManageTriage, incidentHref } from "@/lib/monitoring";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { PageHeader } from "@/components/ui/page-header";

export default function AlertDetailPage() {
  const { alertId } = useParams() as { alertId: string };
  const router = useRouter();

  const { data: alert, isLoading, isError, refetch } = useAlert(alertId);
  const { data: currentUser } = useMe();
  const updateStatusMutation = useUpdateAlertStatus();

  // Role authorization checks
  const isAuthorizedToEdit = canManageTriage(currentUser);

  const handleStatusChange = (newStatus: string) => {
    updateStatusMutation.mutate({ alertId, status: newStatus });
  };

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Alert detail" description="Loading the persisted detection record and its available investigation context." breadcrumb="Alerts / Detail" />

        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-20 bg-zinc-900 rounded-lg" />
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-7">
          <Skeleton className="lg:col-span-4 h-72 bg-zinc-900 rounded-lg" />
          <Skeleton className="lg:col-span-3 h-72 bg-zinc-900 rounded-lg" />
        </div>
      </div>
    );
  }

  // 2. Error State
  if (isError || !alert) {
    return (
      <div className="space-y-6">
        <PageHeader title="Alert detail" description="Review a persisted detection record and its available investigation context." breadcrumb="Alerts / Detail" />
        <OperationalState
          kind="error"
          title="Alert detail is unavailable"
          description="The requested alert could not be retrieved from the backend API."
          action={<div className="flex justify-center gap-2"><Button variant="outline" onClick={() => router.push("/alerts")}>Back to alerts</Button><RetryButton onClick={() => refetch()} /></div>}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={alert.title}
        description={`Alert ID: ${alert.id}`}
        breadcrumb="Alerts / Detail"
        actions={<div className="flex flex-col items-end gap-1.5">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Workflow Status</span>
          {isAuthorizedToEdit ? (
            <div className="flex items-center gap-2">
              <Select
                value={alert.status}
                onValueChange={(val) => val && handleStatusChange(val)}
                disabled={updateStatusMutation.isPending}
              >
                <SelectTrigger className="w-[180px] h-8 bg-zinc-950 border-zinc-900 text-xs">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-950 border-zinc-900 text-xs">
                  <SelectItem value="new">New</SelectItem>
                  <SelectItem value="investigating">Investigating</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="false_positive">False Positive</SelectItem>
                </SelectContent>
              </Select>
              {updateStatusMutation.isPending && (
                <span className="text-[10px] text-indigo-400 animate-pulse">Saving...</span>
              )}
              {updateStatusMutation.isSuccess && (
                <span className="text-[10px] text-emerald-400">Saved</span>
              )}
              {updateStatusMutation.isError && (
                <span className="text-[10px] text-red-400">Failed</span>
              )}
            </div>
          ) : (
            <div className="px-3 py-1.5 border border-zinc-900 bg-zinc-950/40 rounded">
              <StatusIndicator status={alert.status} />
            </div>
          )}
        </div>}
      />
      <Button variant="ghost" className="-mt-4 w-fit" onClick={() => router.push("/alerts")}>
        <ArrowLeft className="mr-1.5 h-3.5 w-3.5" /> Back to alerts
      </Button>

      {/* Metadata Cards Grid */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <Card className="soc-surface gap-0 border-0 py-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Severity</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <SeverityBadge severity={alert.severity} className="text-sm px-2.5 py-1" />
          </CardContent>
        </Card>

        <Card className="soc-surface gap-0 border-0 py-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Correlated incident</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            {alert.incident_id ? (
              <Link className="text-xs font-medium text-primary underline-offset-4 hover:underline" href={incidentHref(alert.incident_id)}>
                Open incident
              </Link>
            ) : (
              <span className="text-xs text-muted-foreground">No linked incident</span>
            )}
          </CardContent>
        </Card>

        <Card className="soc-surface gap-0 border-0 py-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Current Status</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <StatusIndicator status={alert.status} className="text-sm font-semibold" />
          </CardContent>
        </Card>

        <Card className="soc-surface gap-0 border-0 py-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Rule Association</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xs text-zinc-300 font-mono truncate">{alert.rule_id || "N/A"}</div>
          </CardContent>
        </Card>

        <Card className="soc-surface gap-0 border-0 py-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Detection Time</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xs text-zinc-300 font-mono">
              {new Date(alert.created_at).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detail Analysis & MITRE Context */}
      <div className="grid gap-6 lg:grid-cols-7">
        <Card className="soc-surface lg:col-span-4 gap-0 border-0 py-0">
          <CardHeader>
            <CardTitle className="text-sm font-semibold text-zinc-300 uppercase tracking-wider font-mono">
              Why This Triggered
            </CardTitle>
            <CardDescription className="text-xs text-zinc-500 font-mono">
              Signature / heuristic evaluation details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-xs text-zinc-300 leading-relaxed bg-zinc-950 p-4 border border-zinc-900 rounded font-mono">
              {alert.description || "No description provided for this alert."}
            </p>

            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-zinc-400 font-mono uppercase tracking-wider">
                Extracted Indicators
              </h4>
              {alert.indicators_json ? (
                <div className="flex flex-wrap gap-2">
                  {Object.entries(alert.indicators_json).map(([key, val], i) => (
                    <Badge
                      key={i}
                      variant="outline"
                      className="bg-zinc-950 border-zinc-900 text-zinc-300 font-mono text-[11px]"
                    >
                      <span className="text-zinc-500 mr-1">{key}:</span>
                      {String(val)}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-zinc-600 italic font-mono">No distinct entities extracted.</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="soc-surface lg:col-span-3 gap-0 border-0 py-0">
          <CardHeader>
            <CardTitle className="text-sm font-semibold text-zinc-300 uppercase tracking-wider font-mono">
              ATT&CK Context
            </CardTitle>
            <CardDescription className="text-xs text-zinc-500 font-mono">
              MITRE mapping context recommendations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <p className="text-xs text-zinc-400 leading-relaxed font-mono">
                This alert payload does not contain a rule-derived ATT&amp;CK mapping. No technique is inferred by the interface.
              </p>
            </div>

            <div className="space-y-2 border-t border-zinc-900 pt-4">
              <h4 className="text-xs font-semibold text-zinc-400 font-mono uppercase tracking-wider">
                Investigation Guidance
              </h4>
              <p className="text-xs text-zinc-500 leading-relaxed font-mono border-l-2 border-indigo-500 pl-3">
                Use the source event, indicators, and any linked incident to continue the investigation. The API does not provide additional guidance for this alert.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
