import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { WifiOff } from "lucide-react";

interface SourceItem {
  source: string;
  count: number;
}

interface EventSourcesProps {
  sources: SourceItem[];
}

export function EventSources({ sources }: EventSourcesProps) {
  const isEmpty = sources.length === 0;

  return (
    <Card className="bg-zinc-950 border-zinc-900 shadow-none">
      <CardHeader>
        <CardTitle className="text-sm font-semibold text-zinc-300 font-mono uppercase tracking-wider">
          Top Event Sources
        </CardTitle>
        <CardDescription className="text-xs text-zinc-500 font-mono">
          Hosts and services contributing telemetry
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isEmpty ? (
          <div className="flex h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-zinc-800 bg-zinc-950 p-6 text-center">
            <WifiOff className="h-8 w-8 text-zinc-600 mb-3" />
            <p className="text-xs font-mono text-zinc-500 max-w-sm">
              No event sources detected.
            </p>
          </div>
        ) : (
          <div className="max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
            <Table className="border border-zinc-900">
              <TableHeader className="bg-zinc-950/80 sticky top-0 z-10 border-b border-zinc-900">
                <TableRow className="hover:bg-transparent border-zinc-900">
                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-9">Rank</TableHead>
                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-9">Source Name / Address</TableHead>
                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase text-right h-9">Event Count</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sources.map((item, index) => (
                  <TableRow key={index} className="hover:bg-zinc-900/30 border-zinc-900">
                    <TableCell className="font-mono text-zinc-400 text-[11px] py-2">
                      #{index + 1}
                    </TableCell>
                    <TableCell className="font-mono text-zinc-200 text-[11px] font-medium py-2 max-w-[150px] truncate">
                      {item.source || "UNKNOWN"}
                    </TableCell>
                    <TableCell className="font-mono text-zinc-400 text-[11px] text-right py-2">
                      {item.count.toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
