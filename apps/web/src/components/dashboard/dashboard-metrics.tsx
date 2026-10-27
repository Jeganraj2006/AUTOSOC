import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Server, Shield } from "lucide-react";

interface DashboardMetricsProps {
  totalEvents24h: number;
  activeSources: number;
  telemetryCategories: number;
}

export function DashboardMetrics({
  totalEvents24h,
  activeSources,
  telemetryCategories,
}: DashboardMetricsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {/* Total Events */}
      <Card className="soc-surface gap-0 border-0 py-0">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-xs font-semibold tracking-[0.08em] text-muted-foreground uppercase">
            Total Events (24h)
          </CardTitle>
          <Activity className="h-5 w-5 text-primary" aria-hidden="true" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-semibold tracking-[-0.04em] text-foreground tabular-nums">
            {totalEvents24h.toLocaleString()}
          </div>
          <span className="mt-1 block text-xs font-medium text-muted-foreground">
            Ingested security log entries
          </span>
        </CardContent>
      </Card>

      {/* Active Sources */}
      <Card className="soc-surface gap-0 border-0 py-0">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-xs font-semibold tracking-[0.08em] text-muted-foreground uppercase">
            Active Data Sources
          </CardTitle>
          <Server className="h-5 w-5 text-emerald-500" aria-hidden="true" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-semibold tracking-[-0.04em] text-foreground tabular-nums">
            {activeSources}
          </div>
          <span className="mt-1 block text-xs font-medium text-muted-foreground">
            Active logs generators reporting in
          </span>
        </CardContent>
      </Card>

      {/* Telemetry Categories */}
      <Card className="soc-surface gap-0 border-0 py-0">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-xs font-semibold tracking-[0.08em] text-muted-foreground uppercase">
            Telemetry Categories
          </CardTitle>
          <Shield className="h-5 w-5 text-primary" aria-hidden="true" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-semibold tracking-[-0.04em] text-foreground tabular-nums">
            {telemetryCategories}
          </div>
          <span className="mt-1 block text-xs font-medium text-muted-foreground">
            Different normalized message classes
          </span>
        </CardContent>
      </Card>
    </div>
  );
}
