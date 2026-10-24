"use client";

import React, { useState } from "react";
import { useDataSources, DataSource } from "@/hooks/use-data-sources";
import { useMe } from "@/hooks/use-me";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Plus,
  Database,
  AlertCircle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  RefreshCw,
  Edit,
} from "lucide-react";
import { DataSourceDialog } from "@/components/soc/data-source-dialog";

export default function DataSourcesPage() {
  const { data, isLoading, isError, refetch, isFetching } = useDataSources();
  const { data: currentUser } = useMe();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);

  // Authorize managers/administrators
  const isAuthorizedToManage =
    currentUser?.is_superuser ||
    currentUser?.roles.includes("admin") ||
    currentUser?.roles.includes("administrator");

  const handleAddSource = () => {
    setSelectedSource(null);
    setIsDialogOpen(true);
  };

  const handleEditSource = (source: DataSource) => {
    setSelectedSource(source);
    setIsDialogOpen(true);
  };

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="space-y-6 font-mono">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
          <div className="space-y-1">
            <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Data Sources</h2>
            <p className="text-xs text-zinc-500">Monitor and manage log ingestion streams</p>
          </div>
        </div>

        {/* Table Skeleton */}
        <div className="border border-zinc-900 rounded-lg overflow-hidden bg-zinc-950/20">
          <div className="p-4 border-b border-zinc-900 flex gap-4">
            <Skeleton className="h-4 w-40 bg-zinc-900" />
            <Skeleton className="h-4 w-32 bg-zinc-900" />
            <Skeleton className="h-4 w-28 bg-zinc-900" />
            <Skeleton className="h-4 w-20 bg-zinc-900" />
            <Skeleton className="h-4 w-20 bg-zinc-900" />
          </div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 border-b border-zinc-900 flex gap-4 items-center">
              <Skeleton className="h-5 w-40 bg-zinc-900" />
              <Skeleton className="h-5 w-32 bg-zinc-900" />
              <Skeleton className="h-5 w-28 bg-zinc-900" />
              <Skeleton className="h-5 w-20 bg-zinc-900" />
              <Skeleton className="h-5 w-20 bg-zinc-900" />
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
        <h3 className="text-lg font-bold text-red-400">Failed to load data sources</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-2 mb-6">
          Could not communicate with the backend security sources manager.
        </p>
        <Button
          onClick={() => refetch()}
          className="bg-red-950/40 border border-red-900/60 hover:bg-red-900/30 text-red-400 text-xs px-4"
        >
          <RefreshCw className="mr-2 h-3.5 w-3.5" />
          Retry Connection
        </Button>
      </div>
    );
  }

  const items = data?.items || [];

  return (
    <div className="space-y-6 font-mono">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Data Sources</h2>
          <p className="text-xs text-zinc-500 mt-1">
            Monitor and manage log ingestion streams
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

          {isAuthorizedToManage && (
            <Button
              onClick={handleAddSource}
              className="h-8 bg-indigo-650 hover:bg-indigo-700 text-zinc-100 text-xs px-3 font-mono"
            >
              <Plus className="mr-1.5 h-4 w-4" /> Add Source
            </Button>
          )}
        </div>
      </div>

      {/* Observability Table */}
      <div className="border border-zinc-900 rounded-lg overflow-hidden bg-zinc-950/20">
        <Table>
          <TableHeader className="bg-zinc-950/60 border-b border-zinc-900">
            <TableRow className="hover:bg-transparent border-zinc-900">
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-44">Name</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">Type</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-32">Environment</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-24">Enabled</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-32">Health Status</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-40">Last Activity</TableHead>
              {isAuthorizedToManage && (
                <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-20 text-right">Actions</TableHead>
              )}
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.length === 0 ? (
              <TableRow className="hover:bg-transparent border-none">
                <TableCell colSpan={isAuthorizedToManage ? 7 : 6} className="text-center h-48 py-8">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <Database className="h-8 w-8 text-zinc-700" />
                    <p className="text-xs font-semibold text-zinc-400">No data sources configured</p>
                    <p className="text-[11px] text-zinc-650 max-w-xs leading-relaxed mt-0.5">
                      Configure log collection telemetry streams to monitor endpoints.
                    </p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              items.map((source: DataSource) => (
                <TableRow key={source.id} className="hover:bg-zinc-900/20 border-zinc-900">
                  <TableCell className="font-medium text-zinc-200 text-[11px] py-3.5">
                    {source.name}
                  </TableCell>

                  <TableCell className="font-mono text-zinc-400 text-[11px] capitalize py-3.5">
                    {source.source_type.replace("_", " ")}
                  </TableCell>

                  <TableCell className="font-mono text-zinc-400 text-[11px] capitalize py-3.5">
                    {source.environment}
                  </TableCell>

                  <TableCell className="py-3.5">
                    <span
                      className={`inline-flex items-center rounded px-1.5 py-0.5 text-[9px] font-bold font-mono border ${
                        source.enabled
                          ? "bg-indigo-950/20 border-indigo-900/40 text-indigo-400"
                          : "bg-zinc-950 border-zinc-900 text-zinc-550"
                      }`}
                    >
                      {source.enabled ? "Active" : "Disabled"}
                    </span>
                  </TableCell>

                  <TableCell className="py-3.5">
                    {source.status === "healthy" ? (
                      <span className="inline-flex items-center gap-1.5 text-emerald-400 text-[11px]">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                        Healthy
                      </span>
                    ) : source.status === "degraded" ? (
                      <span className="inline-flex items-center gap-1.5 text-amber-400 text-[11px]">
                        <AlertCircle className="h-3.5 w-3.5 text-amber-500" />
                        Degraded
                      </span>
                    ) : source.status === "error" || source.status === "failing" ? (
                      <span className="inline-flex items-center gap-1.5 text-red-400 text-[11px]">
                        <XCircle className="h-3.5 w-3.5 text-red-500 animate-pulse" />
                        Failing
                      </span>
                    ) : source.status === "disabled" ? (
                      <span className="inline-flex items-center gap-1.5 text-zinc-500 text-[11px]">
                        <XCircle className="h-3.5 w-3.5 text-zinc-650" />
                        Disabled
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-zinc-400 text-[11px]">
                        <HelpCircle className="h-3.5 w-3.5 text-zinc-500" />
                        Unknown
                      </span>
                    )}
                  </TableCell>

                  <TableCell className="font-mono text-zinc-500 text-[11px] py-3.5">
                    {source.updated_at ? new Date(source.updated_at).toLocaleString() : "-"}
                  </TableCell>

                  {isAuthorizedToManage && (
                    <TableCell className="py-3.5 text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditSource(source)}
                        className="h-7 w-7 text-zinc-500 hover:text-zinc-100 hover:bg-zinc-900"
                        title="Edit config"
                      >
                        <Edit className="h-3.5 w-3.5" />
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Dialog for Creating and Editing */}
      <DataSourceDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        dataSource={selectedSource}
      />
    </div>
  );
}
