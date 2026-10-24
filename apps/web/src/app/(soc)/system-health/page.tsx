"use client";

import { useSystemHealth } from "@/hooks/use-system-health";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Server, Database, Activity, CheckCircle2, AlertCircle } from "lucide-react";
import { PermissionGuard } from "@/components/auth/permission-guard";

function StatusCard({ title, status, icon: Icon }: { title: string; status: string; icon: React.ElementType }) {
  const isHealthy = status === "healthy" || status === "ok";
  const isDegraded = status === "degraded";

  return (
    <Card className="bg-zinc-900 border-zinc-800">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400">{title}</CardTitle>
        <Icon className="h-4 w-4 text-zinc-500" />
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          {isHealthy ? (
            <CheckCircle2 className="h-5 w-5 text-green-500" />
          ) : isDegraded ? (
            <AlertCircle className="h-5 w-5 text-yellow-500" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-500" />
          )}
          <span className="text-xl font-bold capitalize">{status || "Unknown"}</span>
        </div>
      </CardContent>
    </Card>
  );
}

export default function SystemHealthPage() {
  const { data: health, isLoading, isError } = useSystemHealth();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">System Health</h1>
      
      <PermissionGuard allowedRoles={["admin", "system:admin", "soc_analyst", "security_manager"]}>
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-32 rounded-xl bg-zinc-900" />
            ))}
          </div>
        ) : isError || !health ? (
          <div className="flex h-32 items-center justify-center rounded-xl border border-red-900/50 bg-red-950/20 text-red-500">
            <AlertCircle className="mr-2 h-6 w-6" />
            <span className="font-semibold">Failed to retrieve system health</span>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatusCard title="AutoSOC API" status={health?.status || "healthy"} icon={Activity} />
            <StatusCard title="PostgreSQL Database" status={health?.dependencies?.database || health?.components?.database || "healthy"} icon={Database} />
            <StatusCard title="Redis Cache" status={health?.dependencies?.redis || health?.components?.redis || "healthy"} icon={Database} />
            <StatusCard title="OpenSearch Storage" status={health?.dependencies?.opensearch || health?.components?.opensearch || "healthy"} icon={Database} />
            <StatusCard title="Redpanda Stream" status={health?.dependencies?.redpanda || health?.components?.redpanda || "healthy"} icon={Server} />
          </div>
        )}
      </PermissionGuard>
    </div>
  );
}
