"use client";

import { useMe } from "@/hooks/use-me";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { User, LogOut, Shield } from "lucide-react";
import { signOut } from "next-auth/react";

export default function ProfilePage() {
  const { data: user, isLoading } = useMe();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48 bg-zinc-900" />
        <Skeleton className="h-[400px] w-full max-w-2xl bg-zinc-900" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">User Profile</h1>

      <Card className="bg-zinc-900 border-zinc-800 max-w-2xl">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-zinc-800 ring-4 ring-zinc-950">
              <User className="h-8 w-8 text-zinc-400" />
            </div>
            <div>
              <CardTitle className="text-2xl">{user?.username}</CardTitle>
              <CardDescription className="text-zinc-400">{user?.email}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-1">
            <h3 className="text-sm font-medium text-zinc-500">Authentication Source</h3>
            <p className="text-sm text-zinc-300">Keycloak OIDC (AutoSOC Identity)</p>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-zinc-500">Assigned Roles</h3>
            <div className="flex flex-wrap gap-2">
              {user?.roles.map((role) => (
                <span
                  key={role}
                  className="inline-flex items-center rounded-full border border-blue-900 bg-blue-950/30 px-2.5 py-0.5 text-xs font-semibold text-blue-400"
                >
                  <Shield className="mr-1 h-3 w-3" />
                  {role}
                </span>
              ))}
              {user?.is_superuser && (
                <span className="inline-flex items-center rounded-full border border-purple-900 bg-purple-950/30 px-2.5 py-0.5 text-xs font-semibold text-purple-400">
                  <Shield className="mr-1 h-3 w-3" />
                  superuser
                </span>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-zinc-800">
            <Button
              variant="destructive"
              className="bg-red-950/50 text-red-500 hover:bg-red-900 hover:text-red-100 border border-red-900/50 cursor-pointer"
              onClick={async () => {
                await signOut({ callbackUrl: "/login" });
              }}
            >
              <LogOut className="mr-2 h-4 w-4" /> Sign Out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
