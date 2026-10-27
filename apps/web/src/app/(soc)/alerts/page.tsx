"use client";

import React, { useState } from "react";
import { useAlertSearch } from "@/hooks/use-alerts";
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
import { Input } from "@/components/ui/input";
import { SeverityBadge, StatusIndicator } from "@/components/ui/soc-indicators";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";
import { RefreshCw, XCircle, ArrowRight, ChevronLeft, ChevronRight, Search } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";

export default function AlertsPage() {
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [searchText, setSearchText] = useState("");
  const [offset, setOffset] = useState(0);

  const queryParams = {
    q: searchText.trim() || undefined,
    status: selectedStatus === "all" ? undefined : selectedStatus,
    severity: selectedSeverity === "all" ? undefined : selectedSeverity,
    limit: 50,
    offset,
  };

  const {
    data: alertPage,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useAlertSearch(queryParams);
  const alerts = alertPage?.alerts ?? [];

  const handleClearFilters = () => {
    setSelectedStatus("all");
    setSelectedSeverity("all");
    setSearchText("");
    setOffset(0);
  };

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Alert triage"
          description="Review persisted detections, their current triage status, and available investigation context."
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
            <Skeleton className="h-4 w-24 bg-zinc-900" />
            <Skeleton className="h-4 w-20 bg-zinc-900" />
            <Skeleton className="h-4 w-80 bg-zinc-900" />
            <Skeleton className="h-4 w-32 bg-zinc-900" />
            <Skeleton className="h-4 w-28 bg-zinc-900" />
          </div>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="p-4 border-b border-zinc-900 flex gap-4 items-center">
              <Skeleton className="h-5 w-24 bg-zinc-900" />
              <Skeleton className="h-5 w-20 bg-zinc-900" />
              <Skeleton className="h-5 w-80 bg-zinc-900" />
              <Skeleton className="h-5 w-32 bg-zinc-900" />
              <Skeleton className="h-5 w-28 bg-zinc-900" />
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
          title="Alert triage"
          description="Review persisted detections, their current triage status, and available investigation context."
        />
        <OperationalState
          kind="error"
          title="Alerts are unavailable"
          description="The alert service did not return a usable response. Confirm your session, then retry the request."
          action={<RetryButton onClick={() => refetch()} disabled={isFetching} />}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Alert triage"
        description="Review persisted detections, their current triage status, and available investigation context."
        actions={<div className="flex items-center gap-3">
          <Button
            onClick={() => refetch()}
            disabled={isFetching}
            variant="outline"
            className="h-8 border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 text-xs px-3"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isFetching ? "animate-spin text-indigo-400" : ""}`} />
            Refresh
          </Button>
        </div>}
      />

      {/* Filter Controls Row */}
      <div className="soc-surface flex flex-wrap items-center gap-4 rounded-xl p-4">
        <div className="flex items-center gap-2"><label className="text-[10px] text-zinc-500 uppercase font-semibold" htmlFor="alert-search">Search</label><Input id="alert-search" value={searchText} onChange={(event) => { setSearchText(event.target.value); setOffset(0); }} placeholder="ID, title, description" className="h-8 w-52 text-xs" /><Search className="size-4 text-muted-foreground" aria-hidden="true" /></div>
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Status:</span>
          <Select value={selectedStatus} onValueChange={(val) => val && setSelectedStatus(val)}>
            <SelectTrigger className="w-[160px] h-8 bg-zinc-950 border-zinc-900 text-xs">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-950 border-zinc-900 text-xs">
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="new">New</SelectItem>
              <SelectItem value="investigating">Investigating</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="false_positive">False Positive</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Severity:</span>
          <Select value={selectedSeverity} onValueChange={(val) => val && setSelectedSeverity(val)}>
            <SelectTrigger className="w-[160px] h-8 bg-zinc-950 border-zinc-900 text-xs">
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
        {(selectedStatus !== "all" || selectedSeverity !== "all" || searchText !== "") && (
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

      {/* Alerts Table */}
      <div className="soc-table-wrap">
        <div className="border-b border-border px-4 py-3 text-sm text-muted-foreground">{alertPage?.page.total ?? 0} alerts match the current server-side filter.</div>
        <Table>
          <TableHeader className="bg-zinc-950/60 border-b border-zinc-900">
            <TableRow className="hover:bg-transparent border-zinc-900">
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">Time</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-28">Severity</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10">Alert Description</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-44">Rule ID</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">Status</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-20 text-center">Action</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {alerts.length === 0 ? (
              <TableRow className="hover:bg-transparent border-none">
                <TableCell colSpan={6} className="text-center h-48 py-8">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <XCircle className="h-8 w-8 text-zinc-700" />
                    <p className="text-xs font-semibold text-zinc-400">No alerts found</p>
                    <p className="text-[11px] text-zinc-600 max-w-xs leading-relaxed mt-0.5">
                      Try changing the current filters or wait for new detections.
                    </p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              alerts.map((alert) => (
                <TableRow key={alert.id} className="hover:bg-zinc-900/20 border-zinc-900">
                  <TableCell className="font-mono text-zinc-400 text-[11px] whitespace-nowrap py-3">
                    {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                  </TableCell>

                  <TableCell className="py-3">
                    <SeverityBadge severity={alert.severity} />
                  </TableCell>

                  <TableCell className="py-3 font-medium text-zinc-200 text-[11px] max-w-sm truncate">
                    {alert.title}
                  </TableCell>

                  <TableCell className="font-mono text-zinc-500 text-[11px] truncate py-3 max-w-[150px]">
                    {alert.rule_id || "N/A"}
                  </TableCell>

                  <TableCell className="py-3">
                    <StatusIndicator status={alert.status} />
                  </TableCell>

                  <TableCell className="py-3 text-center">
                    <Link
                      href={`/alerts/${alert.id}`}
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
        <div className="flex justify-end gap-2 border-t border-border px-4 py-3"><Button variant="outline" size="sm" disabled={offset === 0 || isFetching} onClick={() => setOffset((value) => Math.max(0, value - 50))}><ChevronLeft className="mr-1 size-4" />Previous</Button><Button variant="outline" size="sm" disabled={!alertPage || offset + 50 >= alertPage.page.total || isFetching} onClick={() => setOffset((value) => value + 50)}>Next<ChevronRight className="ml-1 size-4" /></Button></div>
      </div>
    </div>
  );
}
