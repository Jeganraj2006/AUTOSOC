"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useDetectAnomalies } from "@/hooks/use-events";
import { Cpu, Shield, Zap, AlertTriangle, CheckCircle2, Activity, Sliders, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function DetectionPage() {
  const [detectionResult, setDetectionResult] = useState<any>(null);
  const detectMutation = useDetectAnomalies();

  const handleRunDetection = () => {
    detectMutation.mutate(100, {
      onSuccess: (data) => {
        setDetectionResult(data);
      },
    });
  };

  const anomalies = detectionResult?.predictions?.filter((p: any) => p.is_anomaly) || [];

  return (
    <div className="flex-1 space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">ML Anomaly Detection Engine</h2>
          <p className="text-xs text-zinc-500 mt-1">
            Isolation Forest ML model for zero-day threat behavior evaluation & anomaly scoring
          </p>
        </div>

        <Button
          onClick={handleRunDetection}
          disabled={detectMutation.isPending}
          className="h-9 bg-rose-950/40 border border-rose-800 text-rose-400 hover:bg-rose-900/40 text-xs px-4 font-mono"
        >
          <Cpu className={`h-4 w-4 mr-2 ${detectMutation.isPending ? "animate-spin" : ""}`} />
          {detectMutation.isPending ? "Fitting Isolation Forest Model..." : "Run ML Anomaly Detection"}
        </Button>
      </div>

      {/* Model Parameter Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-zinc-950/40 border-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-zinc-500 uppercase font-semibold">Model Algorithm</span>
              <Sliders className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="text-lg font-bold text-zinc-100 mt-1">Isolation Forest</div>
            <div className="text-[10px] text-zinc-500 mt-1">Unsupervised Anomaly Detector</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-950/40 border-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-zinc-500 uppercase font-semibold">Contamination Rate</span>
              <Activity className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-lg font-bold text-zinc-100 mt-1">10% (0.10)</div>
            <div className="text-[10px] text-zinc-500 mt-1">Expected Outlier Ratio</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-950/40 border-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-zinc-500 uppercase font-semibold">Evaluated Events</span>
              <Shield className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="text-lg font-bold text-zinc-100 mt-1">
              {detectionResult ? detectionResult.total_events : "100 (Indexed)"}
            </div>
            <div className="text-[10px] text-zinc-500 mt-1">From OpenSearch Storage</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-950/40 border-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-zinc-500 uppercase font-semibold">Anomalies Detected</span>
              <AlertTriangle className="h-4 w-4 text-rose-500" />
            </div>
            <div className="text-lg font-bold text-rose-400 mt-1">
              {detectionResult ? detectionResult.anomalies_detected : "-"}
            </div>
            <div className="text-[10px] text-zinc-500 mt-1">Flagged Outliers</div>
          </CardContent>
        </Card>
      </div>

      {/* Detection Results */}
      {detectionResult && (
        <Card className="bg-zinc-950/40 border-zinc-900">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base text-zinc-100 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-rose-500" />
                  Flagged Anomalous Events ({anomalies.length})
                </CardTitle>
                <CardDescription className="text-xs text-zinc-500 mt-1">
                  Events with Isolation Forest decision score indicating anomalous zero-day pattern deviation.
                </CardDescription>
              </div>
              <span className="text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-900/50 px-2.5 py-1 rounded flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Model Status: Fitted & Evaluated
              </span>
            </div>
          </CardHeader>
          <CardContent>
            {anomalies.length === 0 ? (
              <div className="text-center py-8 text-zinc-500 text-xs">
                No anomalous behavior detected in evaluated events batch.
              </div>
            ) : (
              <div className="space-y-2">
                {anomalies.map((item: any) => (
                  <div
                    key={item.event_id}
                    className="flex items-center justify-between p-3 border border-rose-900/30 rounded bg-rose-950/10 text-xs"
                  >
                    <div className="flex items-center gap-3">
                      <Zap className="h-4 w-4 text-rose-500" />
                      <div>
                        <span className="text-zinc-200 font-bold font-mono">{item.event_id}</span>
                        <div className="text-[10px] text-zinc-500">Model Decision Score: {item.model_score}</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <span className="text-xs font-bold text-rose-400">Score: {item.anomaly_score} / 100</span>
                        <div className="text-[10px] text-zinc-500">High Risk Threshold Exceeded</div>
                      </div>
                      <Link
                        href={`/events/${item.event_id}`}
                        className="inline-flex h-7 w-7 items-center justify-center rounded border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
                      >
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
