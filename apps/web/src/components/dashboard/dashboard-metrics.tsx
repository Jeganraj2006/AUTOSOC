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
    <div className="grid gap-6 md:grid-cols-3">
      {/* Total Events */}
      <Card className="bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-900 shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-xs font-semibold tracking-wider text-slate-500 dark:text-zinc-400 uppercase">
            Total Events (24h)
          </CardTitle>
          <Activity className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-zinc-100">
            {totalEvents24h.toLocaleString()}
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-500 font-medium mt-1 block">
            Ingested security log entries
          </span>
        </CardContent>
      </Card>

      {/* Active Sources */}
      <Card className="bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-900 shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-xs font-semibold tracking-wider text-slate-500 dark:text-zinc-400 uppercase">
            Active Data Sources
          </CardTitle>
          <Server className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-zinc-100">
            {activeSources}
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-500 font-medium mt-1 block">
            Active logs generators reporting in
          </span>
        </CardContent>
      </Card>

      {/* Telemetry Categories */}
      <Card className="bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-900 shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-xs font-semibold tracking-wider text-slate-500 dark:text-zinc-400 uppercase">
            Telemetry Categories
          </CardTitle>
          <Shield className="h-5 w-5 text-sky-600 dark:text-sky-400" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-zinc-100">
            {telemetryCategories}
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-500 font-medium mt-1 block">
            Different normalized message classes
          </span>
        </CardContent>
      </Card>
    </div>
  );
}

