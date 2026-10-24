"use client";

import React, { useState } from "react";
import { useEvents, useUploadEvents, useDetectAnomalies } from "@/hooks/use-events";
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
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { AlertCircle, RefreshCw, XCircle, ArrowRight, ShieldAlert, Search, UploadCloud, FileType, CheckCircle2, Cpu, Zap, AlertTriangle } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

function UploadCsvModal({ onUploadSuccess }: { onUploadSuccess: () => void }) {
  const [open, setOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const uploadMutation = useUploadEvents();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleUpload = () => {
    if (!selectedFile) return;
    uploadMutation.mutate(selectedFile, {
      onSuccess: (data) => {
        setResult(data);
        onUploadSuccess();
      },
    });
  };

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen);
    if (!newOpen) {
      // Reset state when closing
      setSelectedFile(null);
      setResult(null);
      uploadMutation.reset();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger
  render={
    <Button
      variant="outline"
      className="h-8 border-indigo-900/50 bg-indigo-950/20 hover:bg-indigo-900/40 text-indigo-400 hover:text-indigo-300 text-xs px-3"
    >
      <UploadCloud className="h-3.5 w-3.5 mr-1.5" />
      Upload CSV
    </Button>
  }
/>
      <DialogContent className="sm:max-w-md border-zinc-800 bg-zinc-950 font-mono">
        <DialogHeader>
          <DialogTitle className="text-zinc-100 flex items-center">
            <FileType className="h-4 w-4 mr-2 text-indigo-400" />
            Ingest Security Events
          </DialogTitle>
          <DialogDescription className="text-zinc-400 text-xs mt-2">
            Upload a CSV file containing security telemetry to ingest into OpenSearch. The pipeline will automatically map and normalize aliases like src_ip or timestamp.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 py-4">
          {!result ? (
            <>
              <div className="flex items-center justify-center w-full">
                <label
                  htmlFor="dropzone-file"
                  className="flex flex-col items-center justify-center w-full h-32 border-2 border-zinc-800 border-dashed rounded-lg cursor-pointer bg-zinc-950/50 hover:bg-zinc-900/50 transition-colors"
                >
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <UploadCloud className="w-8 h-8 mb-2 text-zinc-500" />
                    <p className="mb-2 text-xs text-zinc-400">
                      <span className="font-semibold text-indigo-400">Click to browse</span> or drag and drop
                    </p>
                    <p className="text-[10px] text-zinc-500">CSV files only</p>
                  </div>
                  <input
                    id="dropzone-file"
                    type="file"
                    accept=".csv,text/csv"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </label>
              </div>

              {selectedFile && (
                <div className="flex items-center justify-between p-2 border border-zinc-800 rounded bg-zinc-900/30">
                  <span className="text-xs text-zinc-300 truncate max-w-[200px]">{selectedFile.name}</span>
                  <span className="text-[10px] text-zinc-500">{(selectedFile.size / 1024).toFixed(1)} KB</span>
                </div>
              )}

              {uploadMutation.isError && (
                <div className="p-3 border border-red-900/50 rounded bg-red-950/20 text-xs text-red-400">
                  {uploadMutation.error instanceof Error ? uploadMutation.error.message : "Upload failed"}
                </div>
              )}

              <Button
                onClick={handleUpload}
                disabled={!selectedFile || uploadMutation.isPending}
                className="w-full bg-indigo-650 hover:bg-indigo-700 text-white font-mono text-xs mt-2"
              >
                {uploadMutation.isPending ? "Ingesting..." : "Ingest Events"}
              </Button>
            </>
          ) : (
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2 p-3 border border-emerald-900/50 rounded bg-emerald-950/20 text-emerald-400">
                <CheckCircle2 className="h-5 w-5" />
                <span className="text-sm font-medium">Ingestion Complete</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 border border-zinc-800 rounded bg-zinc-900/30">
                  <div className="text-zinc-500">Total Rows</div>
                  <div className="text-zinc-200 text-lg">{result.total_rows}</div>
                </div>
                <div className="p-2 border border-emerald-900/50 rounded bg-emerald-950/20">
                  <div className="text-emerald-500/70">Processed</div>
                  <div className="text-emerald-400 text-lg">{result.processed}</div>
                </div>
              </div>
              {result.failed > 0 && (
                <div className="p-2 border border-red-900/50 rounded bg-red-950/20 text-xs">
                  <div className="text-red-500/70">Failed</div>
                  <div className="text-red-400 text-lg">{result.failed}</div>
                  <div className="mt-1 text-[10px] text-red-400/80 line-clamp-2">
                    {result.errors?.[0]}
                  </div>
                </div>
              )}
              <Button onClick={() => handleOpenChange(false)} variant="outline" className="mt-2 text-xs border-zinc-800 hover:bg-zinc-900">
                Close
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function EventsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [sourceIpText, setSourceIpText] = useState<string>("");
  const [limitCount, setLimitCount] = useState<number>(50);

  const [detectionSummary, setDetectionSummary] = useState<any>(null);
  const [anomalyMap, setAnomalyMap] = useState<Map<string, { is_anomaly: boolean; anomaly_score: number }>>(new Map());

  const detectMutation = useDetectAnomalies();

  const queryParams = {
    category: selectedCategory === "all" ? undefined : selectedCategory,
    source_ip: sourceIpText.trim() === "" ? undefined : sourceIpText.trim(),
    limit: limitCount,
  };

  const {
    data,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useEvents(queryParams);

  const handleClearFilters = () => {
    setSelectedCategory("all");
    setSourceIpText("");
    setLimitCount(50);
  };

  const handleSearchTrigger = (e: React.FormEvent) => {
    e.preventDefault();
    refetch();
  };

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="space-y-6 font-mono">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
          <div className="space-y-1">
            <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Log Explorer</h2>
            <p className="text-xs text-zinc-500">Search and investigate security telemetry</p>
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
            <Skeleton className="h-4 w-40 bg-zinc-900" />
            <Skeleton className="h-4 w-20 bg-zinc-900" />
            <Skeleton className="h-4 w-28 bg-zinc-900" />
            <Skeleton className="h-4 w-28 bg-zinc-900" />
            <Skeleton className="h-4 w-16 bg-zinc-900" />
          </div>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="p-4 border-b border-zinc-900 flex gap-4 items-center">
              <Skeleton className="h-5 w-28 bg-zinc-900" />
              <Skeleton className="h-5 w-40 bg-zinc-900" />
              <Skeleton className="h-5 w-20 bg-zinc-900" />
              <Skeleton className="h-5 w-28 bg-zinc-900" />
              <Skeleton className="h-5 w-28 bg-zinc-900" />
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
        <h3 className="text-lg font-bold text-red-400">Unable to load security events</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-2 mb-6">
          There was an error communicating with the OpenSearch upstream log cluster.
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

  const events = data?.events || [];

  const runDetectAnomalies = () => {
    detectMutation.mutate(limitCount, {
      onSuccess: (res) => {
        const map = new Map<string, { is_anomaly: boolean; anomaly_score: number }>();
        res.predictions?.forEach((p: any) => {
          map.set(p.event_id, { is_anomaly: p.is_anomaly, anomaly_score: p.anomaly_score });
        });
        setAnomalyMap(map);
        setDetectionSummary(res);
      },
    });
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Log Explorer</h2>
          <p className="text-xs text-zinc-500 mt-1">
            Search and investigate security telemetry
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={runDetectAnomalies}
            disabled={detectMutation.isPending}
            variant="outline"
            className="h-8 border-rose-900/50 bg-rose-950/20 hover:bg-rose-900/40 text-rose-400 hover:text-rose-300 text-xs px-3 font-mono"
          >
            <Cpu className={`h-3.5 w-3.5 mr-1.5 ${detectMutation.isPending ? "animate-spin" : ""}`} />
            {detectMutation.isPending ? "Analyzing..." : "Detect Anomalies"}
          </Button>

          <UploadCsvModal onUploadSuccess={() => {
            refetch();
            runDetectAnomalies();
          }} />
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

      {/* Filter controls row */}
      <form onSubmit={handleSearchTrigger} className="flex flex-wrap gap-4 items-end bg-zinc-950/40 p-4 border border-zinc-900 rounded-lg">
        {/* Category Filter */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Category:</span>
          <Select value={selectedCategory} onValueChange={(val) => val && setSelectedCategory(val)}>
            <SelectTrigger className="w-[180px] h-8 bg-zinc-950 border-zinc-900 text-xs capitalize">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-950 border-zinc-900 text-xs">
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="authentication">Authentication</SelectItem>
              <SelectItem value="network">Network</SelectItem>
              <SelectItem value="process">Process</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Source IP Filter */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Source IP Address:</span>
          <Input
            placeholder="e.g. 192.168.1.1"
            value={sourceIpText}
            onChange={(e) => setSourceIpText(e.target.value)}
            className="w-[200px] h-8 bg-zinc-950 border-zinc-900 text-xs font-mono focus:border-zinc-800"
          />
        </div>

        {/* Limit Selector */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold">Limit Rows:</span>
          <Select value={limitCount.toString()} onValueChange={(val) => val && setLimitCount(parseInt(val))}>
            <SelectTrigger className="w-[120px] h-8 bg-zinc-950 border-zinc-900 text-xs">
              <SelectValue placeholder="Limit" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-950 border-zinc-900 text-xs">
              <SelectItem value="50">50 rows</SelectItem>
              <SelectItem value="100">100 rows</SelectItem>
              <SelectItem value="500">500 rows</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            type="submit"
            className="h-8 bg-indigo-650 hover:bg-indigo-700 text-zinc-100 text-xs px-3 font-mono"
          >
            <Search className="h-3.5 w-3.5 mr-1.5" />
            Query
          </Button>

          {(selectedCategory !== "all" || sourceIpText !== "" || limitCount !== 50) && (
            <Button
              type="button"
              onClick={handleClearFilters}
              variant="ghost"
              className="h-8 hover:bg-zinc-900 text-zinc-500 hover:text-zinc-300 text-xs px-2.5"
            >
              <XCircle className="h-3.5 w-3.5 mr-1.5 text-zinc-500" />
              Clear Filters
            </Button>
          )}
        </div>
      </form>

      {/* ML Detection Summary Banner */}
      {detectionSummary && (
        <div className="flex items-center justify-between p-3 border border-rose-900/40 bg-rose-950/20 rounded-lg text-xs font-mono">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-rose-500 animate-pulse" />
            <span className="text-zinc-200 font-semibold">ML Detection Summary:</span>
            <span className="text-rose-400 font-bold">{detectionSummary.anomalies_detected} Anomalies</span>
            <span className="text-zinc-500">detected out of {detectionSummary.total_events} events evaluated.</span>
          </div>
          <span className="text-[10px] text-zinc-400 bg-zinc-900 px-2.5 py-1 rounded border border-zinc-800">Model: Isolation Forest</span>
        </div>
      )}

      {/* Events log queue table */}
      <div className="border border-zinc-900 rounded-lg overflow-hidden bg-zinc-950/20">
        <Table>
          <TableHeader className="bg-zinc-950/60 border-b border-zinc-900">
            <TableRow className="hover:bg-transparent border-zinc-900">
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">Time</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">Event ID</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-28">Category</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-28">Type</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-32">Source IP</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-32">Dest IP</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-24">Outcome</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-36">ML Anomaly</TableHead>
              <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-10 w-20 text-center">Action</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {events.length === 0 ? (
              <TableRow className="hover:bg-transparent border-none">
                <TableCell colSpan={9} className="text-center h-48 py-8">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <ShieldAlert className="h-8 w-8 text-zinc-700" />
                    <p className="text-xs font-semibold text-zinc-400">No security events found</p>
                    <p className="text-[11px] text-zinc-600 max-w-xs leading-relaxed mt-0.5">
                      Try adjusting the selected filters or category parameters.
                    </p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              events.map((event) => {
                const anomalyData = anomalyMap.get(event.normalized_event_id);
                return (
                  <TableRow key={event.normalized_event_id} className={`hover:bg-zinc-900/20 border-zinc-900 ${anomalyData?.is_anomaly ? "bg-rose-950/10" : ""}`}>
                    <TableCell className="font-mono text-zinc-400 text-[11px] whitespace-nowrap py-3">
                      {event.event_time ? formatDistanceToNow(new Date(event.event_time), { addSuffix: true }) : "-"}
                    </TableCell>

                    <TableCell className="font-mono text-zinc-500 text-[11px] py-3 max-w-[120px] truncate">
                      {event.normalized_event_id}
                    </TableCell>

                    <TableCell className="py-3 font-medium text-zinc-200 text-[11px] capitalize">
                      {event.event_category}
                    </TableCell>

                    <TableCell className="font-mono text-zinc-400 text-[11px] py-3 capitalize">
                      {event.event_type}
                    </TableCell>

                    <TableCell className="font-mono text-zinc-400 text-[11px] py-3">
                      {event.source_ip || "-"}
                    </TableCell>

                    <TableCell className="font-mono text-zinc-400 text-[11px] py-3">
                      {event.destination_ip || "-"}
                    </TableCell>

                    <TableCell className="py-3">
                      <span
                        className={`inline-flex items-center rounded px-2 py-0.5 text-[10px] font-bold font-mono border uppercase ${
                          event.event_outcome === "success" || event.event_outcome === "allowed"
                            ? "bg-emerald-950/20 border-emerald-900/40 text-emerald-400"
                            : event.event_outcome === "failure" || event.event_outcome === "denied"
                              ? "bg-red-950/20 border-red-900/40 text-red-400"
                              : "bg-zinc-950 border-zinc-900 text-zinc-500"
                        }`}
                      >
                        {event.event_outcome}
                      </span>
                    </TableCell>

                    <TableCell className="py-3 font-mono text-[11px]">
                      {anomalyData ? (
                        anomalyData.is_anomaly ? (
                          <span className="inline-flex items-center gap-1 rounded px-2 py-0.5 text-[10px] font-bold border uppercase bg-rose-950/40 border-rose-800 text-rose-400">
                            <Zap className="h-3 w-3 text-rose-500" />
                            Anomaly ({anomalyData.anomaly_score})
                          </span>
                        ) : (
                          <span className="text-zinc-600 text-[10px]">Normal ({anomalyData.anomaly_score})</span>
                        )
                      ) : (
                        <span className="text-zinc-600 text-[10px]">-</span>
                      )}
                    </TableCell>

                    <TableCell className="py-3 text-center">
                      <Link
                        href={`/events/${event.normalized_event_id}`}
                        className="inline-flex h-6 w-6 items-center justify-center rounded border border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors"
                      >
                        <ArrowRight className="h-3 w-3" />
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
