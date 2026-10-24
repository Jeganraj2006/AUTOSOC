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
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";
import { AlertCircle, RefreshCw, XCircle, ArrowRight, ShieldAlert } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

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
      <div className="space-y-6 font-mono">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
          <div className="space-y-1">
            <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Incidents</h2>
            <p className="text-xs text-zinc-500">Autonomous attack progression & incident queues</p>
          </div>
        </div>

        {/* Filters Skeletons */}
        <div className="flex flex-wrap gap-3 items-center">
          <Skeleton className="h-8 w-44 bg-zinc-900" />
          <Skeleton className="h-8 w-44 bg-zinc-900" />
          <Skeleton className="h-8 w-24 bg-zinc-900" />
        </div>

        {/* Table Skeletons */}
        <div className="border border-zinc-900 rounded-lg overflow-hidden bg-zinc-950/20">
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
      <div className="flex h-[400px] flex-col items-center justify-center rounded-lg border border-red-900/40 bg-red-950/10 p-6 text-center font-mono">
        <AlertCircle className="mb-4 h-12 w-12 text-red-500 animate-pulse" />
        <h3 className="text-lg font-bold text-red-400">Unable to load incidents</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-2 mb-6">
          There was an error communicating with the incidents API. Verify server availability and retry.
        </p>
        <Button
          onClick={() => refetch()}
          className="bg-red-950/40 border border-red-900/60 hover:bg-red-900/30 text-red-400 text-xs px-4"
        >
          <RefreshCw className="mr-2 h-3.5 w-3.5" />
          Retry Request
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Incidents</h2>
          <p className="text-xs text-zinc-500 mt-1">
            Autonomous attack progression & incident queues
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={() => refetch()}
            disabled={isFetching}
            variant="outline"
            className="h-8 border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 text-xs px-3"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isFetching ? "animate-spin text-indigo-400" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filter Controls Row */}
      <div className="flex flex-wrap gap-4 items-center bg-zinc-950/40 p-4 border border-zinc-900 rounded-lg">
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
      <div className="border border-zinc-900 rounded-lg overflow-hidden bg-zinc-950/20">
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
                      href={`/incidents/${incident.id}`}
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
