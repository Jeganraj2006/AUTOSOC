import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, Info } from "lucide-react";

interface SecuritySummaryProps {
  totalEvents24h: number;
  sourcesCount: number;
  categoriesCount: number;
}

export function SecuritySummary({
  totalEvents24h,
  sourcesCount,
  categoriesCount,
}: SecuritySummaryProps) {
  const hasEvents = totalEvents24h > 0;

  return (
    <Card className="bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-900 shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold text-slate-800 dark:text-zinc-300 uppercase tracking-wider">
          Telemetry Activity Summary
        </CardTitle>
        <CardDescription className="text-xs text-slate-500 dark:text-zinc-500 font-medium">
          Diagnostic reporting of ingested telemetry logs
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {hasEvents ? (
          <div className="flex gap-4 items-start border border-indigo-100 dark:border-zinc-900 bg-indigo-50/50 dark:bg-zinc-950 p-4 rounded-xl">
            <div className="rounded-lg bg-indigo-100 dark:bg-indigo-950/40 p-2.5 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-900/50 shrink-0">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-bold text-indigo-950 dark:text-zinc-200">
                Active Telemetry Stream Ingestion
              </p>
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed font-normal">
                The SOC monitoring system is actively ingesting events. A total of{" "}
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">{totalEvents24h.toLocaleString()}</span>{" "}
                log events have been normalized in the last 24 hours. These logs are originating from{" "}
                <span className="text-slate-900 dark:text-zinc-200 font-bold">{sourcesCount}</span> distinct source hosts
                and are classified across{" "}
                <span className="text-slate-900 dark:text-zinc-200 font-bold">{categoriesCount}</span> active security
                categories.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex gap-4 items-start border border-slate-200 dark:border-zinc-900 bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl">
            <div className="rounded-lg bg-slate-100 dark:bg-zinc-900 p-2.5 text-slate-500 dark:text-zinc-500 border border-slate-200 dark:border-zinc-800 shrink-0">
              <Info className="h-6 w-6" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-bold text-slate-700 dark:text-zinc-400">
                Telemetry Silence Detected
              </p>
              <p className="text-xs text-slate-500 dark:text-zinc-500 leading-relaxed">
                No security events were returned by the backend for the selected period. This indicates
                that either no telemetry generators are currently sending data, or the filters are active. Run the demo script to populate telemetry data.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

