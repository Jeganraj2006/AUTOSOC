"use client";

import React, { useState } from "react";
import { useIncidents } from "@/hooks/use-incidents";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { SeverityBadge, StatusIndicator } from "@/components/ui/soc-indicators";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { PageHeader } from "@/components/ui/page-header";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";
import { RefreshCw, XCircle, ArrowRight, ShieldAlert } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { incidentHref } from "@/lib/monitoring";

export default function IncidentsPage() {
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");

  const {
    data: incidents,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useIncidents(0, 100);

  const handleClearFilters = () => {
    setSelectedStatus("all");
    setSelectedSeverity("all");
  };

  // Client-side filtering as backend list API does not support filter parameters
  const filteredIncidents = React.useMemo(() => {
    if (!incidents) return [];
    return incidents.filter((incident) => {
      const matchStatus = selectedStatus === "all" || incident.status === selectedStatus;
      const matchSeverity = selectedSeverity === "all" || incident.severity === selectedSeverity;
      return matchStatus && matchSeverity;
    });
  }, [incidents, selectedStatus, selectedSeverity]);

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Incident workspace"
          description="Track the investigation, approval, and resolution lifecycle for correlated security incidents."
        />

        {/* Filters Skeletons */}
        <div className="flex flex-wrap gap-3 items-center">
          <Skeleton className="h-8 w-44 bg-zinc-900" />
          <Skeleton className="h-8 w-44 bg-zinc-900" />
          <Skeleton className="h-8 w-24 bg-zinc-900" />
        </div>

        {/* Table Skeletons */}
        <div className="soc-table-wrap">
          <div className="p-4 border-b border-zinc-900 flex gap-4">
            <Skeleton className="h-4 w-28 bg-zinc-900" />
            <Skeleton className="h-4 w-64 bg-zinc-900" />
            <Skeleton className="h-4 w-20 bg-zinc-900" />
            <Skeleton className="h-4 w-28 bg-zinc-900" />
            <Skeleton className="h-4 w-16 bg-zinc-900" />
            <Skeleton className="h-4 w-16 bg-zinc-900" />
          </div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 border-b border-zinc-900 flex gap-4 items-center">
              <Skeleton className="h-5 w-28 bg-zinc-900" />
              <Skeleton className="h-5 w-64 bg-zinc-900" />
              <Skeleton className="h-5 w-20 bg-zinc-900" />
              <Skeleton className="h-5 w-28 bg-zinc-900" />
              <Skeleton className="h-5 w-16 bg-zinc-900" />
              <Skeleton className="h-5 w-16 bg-zinc-900" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 2. Error State
  if (isError) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Incident workspace"
          description="Track the investigation, approval, and resolution lifecycle for correlated security incidents."
        />
        <OperationalState
          kind="error"
          title="Incidents are unavailable"
          description="The incident service did not return a usable response. Verify the API connection, then retry the request."
          action={<RetryButton onClick={() => refetch()} disabled={isFetching} />}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Incident workspace"
        description="Track the investigation, approval, and resolution lifecycle for correlated security incidents."
        actions={
          <Button
            onClick={() => refetch()}
            disabled={isFetching}
            variant="outline"
            className="h-9"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isFetching ? "animate-spin text-indigo-400" : ""}`} />
            Refresh
          </Button>
        }
      />

      {/* Filter Controls Row */}
      <div className="soc-surface flex flex-wrap items-center gap-4 rounded-xl p-4">
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Status:</span>
          <Select value={selectedStatus} onValueChange={(val) => val && setSelectedStatus(val)}>
            <SelectTrigger className="w-[180px] h-8 bg-zinc-950 border-zinc-900 text-xs">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-950 border-zinc-900 text-xs">
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="new">New</SelectItem>
              <SelectItem value="triaged">Triaged</SelectItem>
              <SelectItem value="investigating">Investigating</SelectItem>
              <SelectItem value="awaiting_approval">Awaiting Approval</SelectItem>
              <SelectItem value="contained">Contained</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
              <SelectItem value="false_positive">False Positive</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Severity:</span>
          <Select value={selectedSeverity} onValueChange={(val) => val && setSelectedSeverity(val)}>
            <SelectTrigger className="w-[180px] h-8 bg-zinc-950 border-zinc-900 text-xs">
              <SelectValue placeholder="All Severities" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-950 border-zinc-900 text-xs">
              <SelectItem value="all">All Severities</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
              <SelectItem value="informational">Informational</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Reset Buttons */}
        {(selectedStatus !== "all" || selectedSeverity !== "all") && (
          <Button
            onClick={handleClearFilters}
            variant="ghost"
            className="h-8 hover:bg-zinc-900 text-zinc-500 hover:text-zinc-300 text-xs px-2.5"
          >
            <XCircle className="h-3.5 w-3.5 mr-1.5 text-zinc-500" />
            Clear Filters
          </Button>
        )}
      </div>

      {/* Incidents Table */}
      <div className="soc-table-wrap">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-3 text-sm text-muted-foreground">
          <span>{filteredIncidents.length} matching incidents</span>
          <span>Client filters apply to the {incidents?.length ?? 0} records returned by the API.</span>
        </div>
        <Table>
          <TableHeader className="bg-zinc-950/60 border-b border-zinc-900">
            <TableRow className="hover:bg-transparent border-zinc-900">
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">Time</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10">Incident Name</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-28">Severity</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">Status</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-24">Risk Score</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-20 text-center">Alerts</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-20 text-center">Action</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {filteredIncidents.length === 0 ? (
              <TableRow className="hover:bg-transparent border-none">
                <TableCell colSpan={7} className="text-center h-48 py-8">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <ShieldAlert className="h-8 w-8 text-zinc-700" />
                    <p className="text-xs font-semibold text-zinc-400">No incidents found</p>
                    <p className="text-[11px] text-zinc-600 max-w-xs leading-relaxed mt-0.5">
                      No active incidents are currently loaded in the database matching your criteria.
                    </p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              filteredIncidents.map((incident) => (
                <TableRow key={incident.id} className="hover:bg-zinc-900/20 border-zinc-900">
                  <TableCell className="font-mono text-zinc-400 text-[11px] whitespace-nowrap py-3">
                    {formatDistanceToNow(new Date(incident.created_at), { addSuffix: true })}
                  </TableCell>

                  <TableCell className="py-3 font-medium text-zinc-200 text-[11px] max-w-sm truncate">
                    {incident.title}
                  </TableCell>

                  <TableCell className="py-3">
                    <SeverityBadge severity={incident.severity} />
                  </TableCell>

                  <TableCell className="py-3">
                    <StatusIndicator status={incident.status} />
                  </TableCell>

                  <TableCell className="font-mono text-[11px] py-3">
                    <span className={`font-bold ${
                      incident.risk_score >= 80
                        ? "text-red-500"
                        : incident.risk_score >= 50
                        ? "text-amber-500"
                        : "text-zinc-400"
                    }`}>
                      {incident.risk_score.toFixed(1)}
                    </span>
                  </TableCell>

                  <TableCell className="font-mono text-zinc-400 text-[11px] text-center py-3">
                    {incident.alert_count}
                  </TableCell>

                  <TableCell className="py-3 text-center">
                    <Link
                      href={incidentHref(incident.id)}
                      className="inline-flex h-6 w-6 items-center justify-center rounded border border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors"
                    >
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
