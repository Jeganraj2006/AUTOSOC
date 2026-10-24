"use client";

import React from "react";
import { useDashboardSummary, useSeedDashboardTelemetry } from "@/hooks/use-dashboard";
import { useMe } from "@/hooks/use-me";
import { DashboardMetrics } from "@/components/dashboard/dashboard-metrics";
import { EventTimeline } from "@/components/dashboard/event-timeline";
import { EventCategories } from "@/components/dashboard/event-categories";
import { EventSources } from "@/components/dashboard/event-sources";
import { SecuritySummary } from "@/components/dashboard/security-summary";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { AlertCircle, DatabaseZap, RefreshCw } from "lucide-react";
import { format } from "date-fns";

export default function DashboardPage() {
  const {
    data: summary,
    isLoading,
    isError,
    refetch,
    isFetching,
    dataUpdatedAt,
  } = useDashboardSummary();
  const { data: currentUser } = useMe();
  const seedTelemetry = useSeedDashboardTelemetry();

  const handleRefresh = async () => {
    await refetch();
  };

  const canSeedDemoTelemetry =
    process.env.NODE_ENV !== "production" &&
    (currentUser?.is_superuser || currentUser?.roles.includes("administrator"));

  const handleSeedDemoTelemetry = async () => {
    await seedTelemetry.mutateAsync();
  };

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
          <div className="space-y-2">
            <Skeleton className="h-8 w-64 bg-zinc-900" />
            <Skeleton className="h-4 w-96 bg-zinc-900" />
          </div>
          <Skeleton className="h-9 w-28 bg-zinc-900" />
        </div>

        {/* Metrics Grid Skeleton */}
        <div className="grid gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28 bg-zinc-900 rounded-lg" />
          ))}
        </div>

        {/* Charts & Table Skeleton */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-[400px] bg-zinc-900 rounded-lg" />
          <Skeleton className="h-[400px] bg-zinc-900 rounded-lg" />
        </div>
      </div>
    );
  }

  // 2. Error State
  if (isError || !summary) {
    return (
      <div className="flex h-[450px] flex-col items-center justify-center rounded-lg border border-red-900/40 bg-red-950/10 p-6 text-center font-mono">
        <AlertCircle className="mb-4 h-12 w-12 text-red-500 animate-pulse" />
        <h3 className="text-lg font-bold text-red-400">Unable to load security telemetry</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-2 mb-6">
          The dashboard request failed. Please verify that the API backend is active and that your session is valid.
        </p>
        <Button
          onClick={handleRefresh}
          className="bg-red-950/40 border border-red-900/60 hover:bg-red-900/30 text-red-400 text-xs px-4"
        >
          <RefreshCw className="mr-2 h-3.5 w-3.5" />
          Retry Connection
        </Button>
      </div>
    );
  }

  // Derive counts
  const totalEvents = summary.total_events_24h || 0;
  const sourcesCount = summary.sources?.length || 0;
  const categoriesCount = summary.categories?.length || 0;

  return (
    <div className="space-y-6 relative">

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">
            Security Operations Center
          </h2>
          <p className="text-xs text-zinc-500 mt-1">
            Real-time security monitoring and threat visibility
          </p>
        </div>

        <div className="flex items-center gap-3">
          {dataUpdatedAt && (
            <div className="text-[10px] text-zinc-600 text-right mr-2">
              {isFetching ? (
                <span className="text-zinc-500 animate-pulse">Synchronizing stream...</span>
              ) : (
                <span>Last updated: {format(new Date(dataUpdatedAt), "HH:mm:ss")}</span>
              )}
            </div>
          )}

          <Button
            onClick={handleRefresh}
            disabled={isFetching}
            variant="outline"
            className="h-8 border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 text-xs px-3"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isFetching ? "animate-spin text-indigo-400" : ""}`} />
            Refresh
          </Button>

          {canSeedDemoTelemetry && (
            <Button
              onClick={handleSeedDemoTelemetry}
              disabled={seedTelemetry.isPending}
              variant="outline"
              className="h-8 border-indigo-900/70 bg-indigo-950/30 hover:bg-indigo-900/40 text-indigo-300 text-xs px-3"
            >
              <DatabaseZap className={`h-3.5 w-3.5 mr-1.5 ${seedTelemetry.isPending ? "animate-pulse" : ""}`} />
              {seedTelemetry.isPending ? "Loading sample data..." : "Load sample data"}
            </Button>
          )}


        </div>
      </div>

      {/* Metrics Row */}
      <DashboardMetrics
        totalEvents24h={totalEvents}
        activeSources={sourcesCount}
        telemetryCategories={categoriesCount}
      />

      {/* Main Insights Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Event Timeline */}
        <div className="lg:col-span-2">
          <EventTimeline timeline={summary.timeline || []} />
        </div>

        {/* Categories Distribution */}
        <EventCategories categories={summary.categories || []} />

        {/* Event Sources */}
        <EventSources sources={summary.sources || []} />
      </div>

      {/* Diagnostic Coverage Summary */}
      <SecuritySummary
        totalEvents24h={totalEvents}
        sourcesCount={sourcesCount}
        categoriesCount={categoriesCount}
      />
    </div>
  );
}
