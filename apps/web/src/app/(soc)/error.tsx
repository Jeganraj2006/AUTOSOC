"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Optionally log to an error reporting service
    console.error("Global boundary caught:", error);
  }, [error]);

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center p-6 text-center">
      <div className="rounded-full bg-red-950/30 p-4 ring-1 ring-red-900/50">
        <AlertCircle className="h-10 w-10 text-red-500" />
      </div>
      <h2 className="mt-4 text-xl font-semibold text-zinc-100">
        Something went wrong
      </h2>
      <p className="mt-2 text-sm text-zinc-400 max-w-md">
        An unexpected error occurred while rendering this page. The issue has been logged.
      </p>
      {error.digest && (
        <p className="mt-2 text-xs font-mono text-zinc-600">
          Error ID: {error.digest}
        </p>
      )}
      <Button
        onClick={() => reset()}
        variant="outline"
        className="mt-6 border-zinc-700 bg-zinc-800 text-zinc-100 hover:bg-zinc-700 hover:text-white"
      >
        Try again
      </Button>
    </div>
  );
}
