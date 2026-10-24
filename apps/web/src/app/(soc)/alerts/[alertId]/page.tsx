"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import { useAlert, useUpdateAlertStatus } from "@/hooks/use-alerts";
import { useMe } from "@/hooks/use-me";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { SeverityBadge, StatusIndicator } from "@/components/ui/soc-indicators";
import { ArrowLeft, AlertCircle, RefreshCw } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function AlertDetailPage() {
  const { alertId } = useParams() as { alertId: string };
  const router = useRouter();

  const { data: alert, isLoading, isError, refetch } = useAlert(alertId);
  const { data: currentUser } = useMe();
  const updateStatusMutation = useUpdateAlertStatus();

  // Role authorization checks
  const isAuthorizedToEdit =
    currentUser?.is_superuser ||
    currentUser?.roles.includes("admin") ||
    currentUser?.roles.includes("soc_analyst");

  const handleStatusChange = (newStatus: string) => {
    updateStatusMutation.mutate({ alertId, status: newStatus });
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
      <div className="flex h-[400px] flex-col items-center justify-center rounded-lg border border-red-900/40 bg-red-950/10 p-6 text-center font-mono">
        <AlertCircle className="mb-4 h-12 w-12 text-red-500" />
        <h3 className="text-lg font-bold text-red-400">Alert not found</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-2 mb-6">
          The requested alert details could not be retrieved from the backend API.
        </p>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => router.push("/alerts")}
            variant="outline"
            className="border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-xs"
          >
            Back to Alerts
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
    <div className="space-y-6 font-mono">
      {/* Header / Actions Block */}
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between border-b border-zinc-900 pb-4">
        <div className="space-y-2">
          <button
            onClick={() => router.push("/alerts")}
            className="inline-flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Alerts
          </button>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">{alert.title}</h2>
          <p className="text-xs text-zinc-500">ID: {alert.id}</p>
        </div>

        {/* Status Update Control Section */}
        <div className="flex flex-col items-end gap-1.5">
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
        </div>
      </div>

      {/* Metadata Cards Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Severity</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <SeverityBadge severity={alert.severity} className="text-sm px-2.5 py-1" />
          </CardContent>
        </Card>

        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Current Status</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <StatusIndicator status={alert.status} className="text-sm font-semibold" />
          </CardContent>
        </Card>

        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">Rule Association</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xs text-zinc-300 font-mono truncate">{alert.rule_id || "N/A"}</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-950 border-zinc-900 shadow-none">
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
        <Card className="lg:col-span-4 bg-zinc-950 border-zinc-900 shadow-none">
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

        <Card className="lg:col-span-3 bg-zinc-950 border-zinc-900 shadow-none">
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
                The evaluation signature tags suggest association with the following threat technique:
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge className="bg-indigo-950/40 border border-indigo-900/60 text-indigo-400 font-mono text-xs">
                  T1110 (Credential Access)
                </Badge>
              </div>
            </div>

            <div className="space-y-2 border-t border-zinc-900 pt-4">
              <h4 className="text-xs font-semibold text-zinc-400 font-mono uppercase tracking-wider">
                Investigation Guidance
              </h4>
              <p className="text-xs text-zinc-500 leading-relaxed font-mono border-l-2 border-indigo-500 pl-3">
                Review syslog event streams around detection timestamp. Check IP address reputation and verify if subsequent target authentication requests completed successfully.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
