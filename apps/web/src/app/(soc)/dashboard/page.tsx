"use client";

import React from "react";
import { useDashboardOperations, useDashboardSummary, useSeedDashboardTelemetry } from "@/hooks/use-dashboard";
import { useSystemHealth } from "@/hooks/use-system-health";
import { useMe } from "@/hooks/use-me";
import { DashboardMetrics } from "@/components/dashboard/dashboard-metrics";
import { EventTimeline } from "@/components/dashboard/event-timeline";
import { EventCategories } from "@/components/dashboard/event-categories";
import { EventSources } from "@/components/dashboard/event-sources";
import { SecuritySummary } from "@/components/dashboard/security-summary";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { DatabaseZap, RefreshCw } from "lucide-react";
import { format } from "date-fns";
import { PageHeader } from "@/components/ui/page-header";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";
import { OperationsOverview } from "@/components/dashboard/operations-overview";

export default function DashboardPage() {
  const {
    data: summary,
    isLoading,
    isError,
    refetch,
    isFetching,
    dataUpdatedAt,
  } = useDashboardSummary();
  const { data: operations, isLoading: operationsLoading, isError: operationsError } = useDashboardOperations();
  const { data: systemHealth, isLoading: healthLoading, isError: healthError } = useSystemHealth();
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
      <OperationalState
        kind="error"
        title="Unable to load security telemetry"
        description="The dashboard request failed. Verify that the API is active and that your session is still valid."
        action={<RetryButton onClick={handleRefresh} />}
      />
    );
  }

  // Derive counts
  const totalEvents = summary.total_events_24h || 0;
  const sourcesCount = summary.sources?.length || 0;
  const categoriesCount = summary.categories?.length || 0;
  const activeAlerts = operations?.open_alert_count ?? undefined;
  const criticalIncidents = operations?.critical_incident_count ?? undefined;

  return (
    <div className="relative space-y-6">

      <PageHeader
        title="Security operations"
        description="Operational telemetry from the authenticated AutoSOC event pipeline."
        actions={
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
            className="h-9"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isFetching ? "animate-spin text-indigo-400" : ""}`} />
            Refresh
          </Button>

          {canSeedDemoTelemetry ? (
            <Button
              onClick={handleSeedDemoTelemetry}
              disabled={seedTelemetry.isPending}
              variant="outline"
              className="h-9"
            >
              <DatabaseZap className={`h-3.5 w-3.5 mr-1.5 ${seedTelemetry.isPending ? "animate-pulse" : ""}`} />
              {seedTelemetry.isPending ? "Loading sample data..." : "Load sample data"}
            </Button>
          ) : null}
          </div>
        }
      />

      {/* Metrics Row */}
      <DashboardMetrics
        totalEvents24h={totalEvents}
        activeSources={sourcesCount}
        telemetryCategories={categoriesCount}
      />

      <OperationsOverview
        activeAlerts={activeAlerts}
        criticalIncidents={criticalIncidents}
        sourceCount={operations?.ingestion_sources.length ?? sourcesCount}
        healthStatus={systemHealth?.status}
        pendingApprovals={operations?.pending_approval_count ?? undefined}
        completedInvestigations={operations?.completed_investigation_count ?? undefined}
        runningInvestigations={operations?.running_investigation_count ?? undefined}
        failedInvestigations={operations?.failed_investigation_count ?? undefined}
        isLoading={operationsLoading || healthLoading}
        unavailable={operationsError || healthError}
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
