"use client";

import { Card } from "@/components/ui/card";

import { PermissionGuard } from "@/components/auth/permission-guard";
import { ShieldCheck } from "lucide-react";

export default function AuditPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Audit Activity</h1>
      
      <PermissionGuard
        allowedRoles={["admin", "system:admin"]}
        requireSuperuser
        fallback={
          <div className="flex h-[300px] items-center justify-center rounded-xl border border-red-900/50 bg-red-950/20 text-red-500">
            Permission Denied. Only administrators can view audit logs.
          </div>
        }
      >
        <Card className="bg-zinc-900 border-zinc-800 flex h-[300px] flex-col items-center justify-center p-6 text-center text-zinc-500">
          <ShieldCheck className="mb-4 h-12 w-12 text-zinc-600" />
          <h2 className="text-lg font-semibold text-zinc-300">Audit Logging Enabled</h2>
          <p className="text-sm max-w-md mt-2">
            Audit events are securely written to the database. The frontend viewer for these events is pending backend API finalization in a future phase.
          </p>
        </Card>
      </PermissionGuard>
    </div>
  );
}
