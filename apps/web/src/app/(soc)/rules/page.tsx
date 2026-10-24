"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { PermissionGuard } from "@/components/auth/permission-guard";

interface RuleResponse {
  id: string;
  name: string;
  rule_type: string;
  severity: string;
  enabled: boolean;
  version: string;
}

export default function RulesPage() {
  const { data: rules, isLoading, error } = useQuery<RuleResponse[]>({
    queryKey: ["rules"],
    queryFn: () => fetchApi("/rules?limit=100"),
  });

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Detection Rules</h2>
      </div>
      
      <PermissionGuard
        allowedRoles={["admin"]}
        fallback={
          <div className="p-8 text-center text-muted-foreground border rounded-md">
            You do not have permission to view or manage detection rules.
          </div>
        }
      >
        <div className="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Version</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center h-24">Loading rules...</TableCell>
                </TableRow>
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-destructive h-24">Error loading rules.</TableCell>
                </TableRow>
              ) : !rules || rules.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center h-24">No rules registered.</TableCell>
                </TableRow>
              ) : (
                rules.map((rule) => (
                  <TableRow key={rule.id}>
                    <TableCell className="font-medium">{rule.name}</TableCell>
                    <TableCell className="capitalize">{rule.rule_type}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{rule.severity}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={rule.enabled ? "default" : "secondary"}>
                        {rule.enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </TableCell>
                    <TableCell>{rule.version}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </PermissionGuard>
    </div>
  );
}
