"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  BrainCircuit,
  RefreshCw,
  AlertCircle,
  ArrowRight,
  TrendingUp,
  Target,
  History,
  ExternalLink,
  Shield,
  Activity,
  FileText,
  Search,
  Loader2,
  Calendar,
  Layers,
} from "lucide-react";

import { getMitreTitle } from "@/lib/mitre-utils";
import { useIncidents, IncidentResponse } from "@/hooks/use-incidents";
import { useLatestPrediction, useAllPredictions, useRecomputePrediction } from "@/hooks/use-predictions";
import { useMe } from "@/hooks/use-me";
import Link from "next/link";

export default function PredictionsPage() {
  const { data: currentUser } = useMe();
  const { data: incidentsData, isLoading: isIncidentsLoading, isError: isIncidentsError, refetch: refetchIncidents } = useIncidents(0, 100);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Automatically select the first incident when data loads
  React.useEffect(() => {
    if (!selectedIncidentId && incidentsData && incidentsData.length > 0) {
      setSelectedIncidentId(incidentsData[0].id);
    }
  }, [incidentsData, selectedIncidentId]);

  const selectedIncident = incidentsData?.find((i: IncidentResponse) => i.id === selectedIncidentId);

  // Fetch prediction details and history if selected
  const {
    data: latestPrediction,
    isLoading: isPredictionLoading,
    isError: isPredictionError,
    refetch: refetchLatestPrediction,
    isFetching: isPredictionFetching,
  } = useLatestPrediction(selectedIncidentId || "");

  const {
    data: predictionsHistory,
    isLoading: isHistoryLoading,
    isError: isHistoryError,
  } = useAllPredictions(selectedIncidentId || "");

  const recomputeMutation = useRecomputePrediction();

  // Authorize manual trigger
  const isAuthorizedToRecompute =
    !!(currentUser?.is_superuser ||
    currentUser?.roles?.includes("admin") ||
    currentUser?.roles?.includes("soc_analyst"));

  const handleRecompute = () => {
    if (!selectedIncidentId) return;
    recomputeMutation.mutate(selectedIncidentId, {
      onSuccess: () => {
        refetchLatestPrediction();
      },
    });
  };

  const isRecomputing = recomputeMutation.isPending;

  // Filter incidents client-side
  const filteredIncidents = incidentsData?.filter((incident: IncidentResponse) => {
    const matchesSearch = incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  }) || [];

  return (
    <div className="space-y-6 font-mono pb-12">
      {/* Header Block */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">Attack Progression Predictions</h2>
          <p className="text-xs text-zinc-500 mt-1">
            Predicted next-stage attack techniques and threat progression forecasts
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Side: Incident Selector Queue */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="bg-zinc-950 border-zinc-900 shadow-none flex flex-col h-[70vh]">
            <CardHeader className="p-4 border-b border-zinc-900">
              <CardTitle className="text-xs font-bold text-zinc-400 uppercase tracking-wider font-mono">
                Recent Incidents
              </CardTitle>
              <CardDescription className="text-[10px] text-zinc-650 font-mono">
                Select an incident to view predictions
              </CardDescription>
              <div className="relative mt-2">
                <Search className="absolute left-2 top-2.5 h-3.5 w-3.5 text-zinc-600" />
                <Input
                  placeholder="Filter incidents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-8 pl-8 bg-zinc-950 border-zinc-900 text-xs font-mono focus:border-zinc-800"
                />
              </div>
            </CardHeader>

            <CardContent className="p-2 overflow-y-auto flex-1 divide-y divide-zinc-900">
              {isIncidentsLoading ? (
                <div className="py-8 text-center text-zinc-650 text-xs">
                  <Loader2 className="mx-auto h-5 w-5 animate-spin mb-2 text-indigo-400" />
                  Loading queue...
                </div>
              ) : isIncidentsError ? (
                <div className="p-4 text-center text-red-500 text-xs space-y-2">
                  <AlertCircle className="mx-auto h-5 w-5 text-red-500" />
                  <div>Failed to fetch incidents.</div>
                  <Button
                    onClick={() => refetchIncidents()}
                    variant="ghost"
                    className="h-6 text-zinc-500 hover:text-zinc-300 text-[10px] uppercase border border-zinc-900"
                  >
                    Retry
                  </Button>
                </div>
              ) : filteredIncidents.length === 0 ? (
                <div className="py-12 text-center text-zinc-650 text-xs font-mono">
                  No matching incidents found.
                </div>
              ) : (
                filteredIncidents.map((incident: IncidentResponse) => (
                  <button
                    key={incident.id}
                    onClick={() => setSelectedIncidentId(incident.id)}
                    className={`w-full text-left p-3 transition-colors ${
                      selectedIncidentId === incident.id
                        ? "bg-zinc-900/40 border-l-2 border-indigo-500 text-zinc-100"
                        : "hover:bg-zinc-900/10 text-zinc-400 hover:text-zinc-200"
                    }`}
                  >
                    <div className="flex justify-between items-start gap-2">
                      <span className="font-bold text-[11px] truncate max-w-[150px] uppercase font-mono">
                        {incident.title}
                      </span>
                      <span
                        className={`text-[8px] font-bold px-1 rounded border uppercase font-mono ${
                          incident.severity === "critical"
                            ? "bg-red-950/20 border-red-900/40 text-red-400"
                            : incident.severity === "high"
                            ? "bg-orange-950/20 border-orange-900/40 text-orange-400"
                            : incident.severity === "medium"
                            ? "bg-yellow-950/20 border-yellow-900/40 text-yellow-400"
                            : "bg-zinc-950 border-zinc-900 text-zinc-400"
                        }`}
                      >
                        {incident.severity}
                      </span>
                    </div>
                    <div className="text-[9px] text-zinc-500 mt-1 truncate">ID: {incident.id.slice(0, 8)}...</div>
                    <div className="flex justify-between items-center text-[9px] text-zinc-600 mt-2 font-mono">
                      <span>Risk: {incident.risk_score}</span>
                      <span>Alerts: {incident.alert_count}</span>
                    </div>
                  </button>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Side: Prediction Details Workspace */}
        <div className="lg:col-span-3 space-y-6">
          {!selectedIncidentId ? (
            <Card className="bg-zinc-950 border-zinc-900 shadow-none border-dashed p-16 text-center h-[70vh] flex flex-col items-center justify-center">
              <BrainCircuit className="h-10 w-10 text-zinc-700 mb-3" />
              <p className="text-xs font-semibold text-zinc-400">No Incident Selected</p>
              <p className="text-[10px] text-zinc-600 max-w-sm mt-1 leading-relaxed">
                Select an incident from the left-side queue to query and visualize transition probabilities and forecasted next attack tactics.
              </p>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* Incident Context Panel */}
              <Card className="bg-zinc-950 border-zinc-900 shadow-none">
                <CardHeader className="p-4 border-b border-zinc-900 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                  <div>
                    <span className="text-[9px] text-zinc-500 uppercase tracking-widest font-mono">
                      Active Workspace
                    </span>
                    <CardTitle className="text-sm font-bold text-zinc-200 uppercase tracking-wider font-mono mt-1">
                      {selectedIncident?.title || "Incident Prediction Details"}
                    </CardTitle>
                    <div className="text-[9px] text-zinc-600 font-mono mt-0.5">
                      Incident UUID: {selectedIncidentId}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link href={`/incidents/${selectedIncidentId}`} passHref>
                      <Button
                        variant="outline"
                        className="h-8 border-zinc-900 bg-zinc-950 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 text-xs px-3 font-mono"
                      >
                        <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
                        Incident Workspace
                      </Button>
                    </Link>

                    <Button
                      onClick={handleRecompute}
                      disabled={isRecomputing || isPredictionFetching}
                      className="h-8 bg-indigo-650 hover:bg-indigo-700 disabled:bg-indigo-900 text-zinc-100 text-xs px-3 font-mono"
                    >
                      {isRecomputing ? (
                        <>
                          <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                          Recomputing...
                        </>
                      ) : (
                        <>
                          <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isPredictionFetching ? "animate-spin" : ""}`} />
                          Recompute Forecast
                        </>
                      )}
                    </Button>
                  </div>
                </CardHeader>

                <CardContent className="p-4">
                  {isPredictionLoading ? (
                    <div className="py-16 text-center text-zinc-500">
                      <Loader2 className="mx-auto h-6 w-6 animate-spin mb-2 text-indigo-400" />
                      Loading forecast metrics...
                    </div>
                  ) : isPredictionError ? (
                    <div className="rounded border border-red-900/40 bg-red-950/10 p-6 text-center text-red-500 text-xs">
                      <AlertCircle className="mx-auto h-6 w-6 mb-2" />
                      No active attack progression prediction recorded for this incident yet.
                      <div className="mt-4">
                        <Button
                          onClick={handleRecompute}
                          disabled={isRecomputing}
                          className="h-7 bg-indigo-650 hover:bg-indigo-700 text-zinc-100 text-xs px-3 font-mono"
                        >
                          Trigger Initial Forecast
                        </Button>
                      </div>
                    </div>
                  ) : latestPrediction ? (
                    <div className="space-y-6">
                      {/* Prediction Factual Metrics Grid */}
                      <div className="grid gap-4 grid-cols-2 md:grid-cols-4 bg-zinc-950/40 p-4 border border-zinc-900 rounded">
                        <div>
                          <div className="text-[9px] text-zinc-650 uppercase font-semibold">Escalation Risk</div>
                          <div className="flex items-center gap-2 mt-1.5">
                            <span
                              className={`text-[12px] font-bold font-mono ${
                                latestPrediction.escalation_risk_score >= 0.7
                                  ? "text-red-400"
                                  : latestPrediction.escalation_risk_score >= 0.4
                                  ? "text-amber-400"
                                  : "text-emerald-400"
                              }`}
                            >
                              {(latestPrediction.escalation_risk_score * 100).toFixed(0)}%
                            </span>
                            <div className="flex-1 h-1.5 bg-zinc-900 rounded overflow-hidden max-w-[80px]">
                              <div
                                className={`h-full rounded ${
                                  latestPrediction.escalation_risk_score >= 0.7
                                    ? "bg-red-500"
                                    : latestPrediction.escalation_risk_score >= 0.4
                                    ? "bg-amber-500"
                                    : "bg-emerald-500"
                                }`}
                                style={{ width: `${latestPrediction.escalation_risk_score * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>

                        <div>
                          <div className="text-[9px] text-zinc-650 uppercase font-semibold">Model Confidence</div>
                          <span
                            className={`inline-flex items-center rounded mt-1 px-1.5 py-0.25 text-[9px] font-bold border uppercase ${
                              latestPrediction.confidence === "high"
                                ? "bg-emerald-950/20 border-emerald-900/40 text-emerald-400"
                                : latestPrediction.confidence === "medium"
                                ? "bg-amber-950/20 border-amber-900/40 text-amber-400"
                                : "bg-zinc-950 border-zinc-900 text-zinc-400"
                            }`}
                          >
                            {latestPrediction.confidence || "unknown"}
                          </span>
                        </div>

                        <div>
                          <div className="text-[9px] text-zinc-650 uppercase font-semibold">Model Identifier</div>
                          <div className="text-[11px] text-zinc-300 mt-1 truncate">
                            {latestPrediction.model_name || "-"} ({latestPrediction.model_version || "-"})
                          </div>
                        </div>

                        <div>
                          <div className="text-[9px] text-zinc-650 uppercase font-semibold">Last Forecast Run</div>
                          <div className="text-[10px] text-zinc-400 mt-1">
                            {new Date(latestPrediction.generated_at).toLocaleString()}
                          </div>
                        </div>
                      </div>

                      {/* Forecast disclaimer limitations */}
                      {latestPrediction.limitations && (
                        <div className="p-3 bg-zinc-950/50 border border-zinc-900 rounded text-zinc-550 flex items-start gap-2">
                          <Shield className="h-4 w-4 shrink-0 text-zinc-700 mt-0.5" />
                          <div className="text-[10px] leading-relaxed">
                            <span className="font-bold text-zinc-500">Forecasting Limitations:</span>{" "}
                            {latestPrediction.limitations}
                          </div>
                        </div>
                      )}

                      {/* Visual MITRE ATT&CK Progression Flow */}
                      <div className="space-y-3 pt-2">
                        <div className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider border-b border-zinc-900 pb-1 flex items-center gap-1.5">
                          <Layers className="h-3.5 w-3.5" />
                          Markov Chain Progression Flow
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Left Column: Observed Techniques */}
                          <div className="border border-zinc-900 bg-zinc-950/20 rounded p-4">
                            <div className="text-[9px] text-zinc-600 uppercase font-semibold border-b border-zinc-900 pb-1.5">
                              Current Observed Stages
                            </div>
                            <div className="mt-3 space-y-2 max-h-[220px] overflow-y-auto">
                              {latestPrediction.observed_techniques?.length === 0 ? (
                                <div className="text-[10px] text-zinc-650 italic">No MITRE techniques observed yet.</div>
                              ) : (
                                latestPrediction.observed_techniques?.map((tech) => (
                                  <div
                                    key={tech}
                                    className="flex items-center justify-between bg-zinc-900/40 border border-zinc-900/50 px-2.5 py-1.5 rounded text-[11px] text-zinc-300 font-mono"
                                  >
                                    <div className="flex items-center gap-2">
                                      <span className="text-zinc-500 font-bold shrink-0">CODE:</span>
                                      <span className="text-zinc-200">{tech}</span>
                                    </div>
                                    <span className="text-[10px] text-zinc-400 font-sans font-medium">
                                      {getMitreTitle(tech)}
                                    </span>
                                  </div>
                                ))
                              )}
                            </div>
                          </div>

                          {/* Right Column: Predicted Next Techniques */}
                          <div className="border border-zinc-900 bg-zinc-950/20 rounded p-4">
                            <div className="text-[9px] text-zinc-600 uppercase font-semibold border-b border-zinc-900 pb-1.5">
                              Estimated Next Stage Candidates
                            </div>
                            <div className="mt-3 space-y-3 max-h-[220px] overflow-y-auto">
                              {latestPrediction.predicted_next_techniques?.length === 0 ? (
                                <div className="text-[10px] text-zinc-650 italic">No transition candidates computed.</div>
                              ) : (
                                latestPrediction.predicted_next_techniques?.map((pred) => (
                                  <div
                                    key={pred.technique_id}
                                    className="border border-zinc-900 bg-zinc-950 p-3 rounded space-y-2"
                                  >
                                    <div className="flex items-center justify-between">
                                      <div className="flex items-center gap-2">
                                        <span className="font-bold text-[11px] text-indigo-400 font-mono">{pred.technique_id}</span>
                                        <span className="text-[10px] text-zinc-300 font-sans font-semibold">
                                          ({getMitreTitle(pred.technique_id)})
                                        </span>
                                      </div>
                                      {pred.probability !== undefined && (
                                        <span className="text-[10px] font-bold text-zinc-300 font-mono">
                                          {(pred.probability * 100).toFixed(0)}% Probability
                                        </span>
                                      )}
                                    </div>

                                    {pred.predicted_tactic && (
                                      <div className="text-[9px] text-zinc-500">
                                        Tactic: <span className="font-bold uppercase text-zinc-400">{pred.predicted_tactic}</span>
                                      </div>
                                    )}

                                    {pred.defensive_recommendation && (
                                      <div className="text-[10px] text-zinc-400 bg-zinc-900/30 p-2 border border-zinc-900 rounded leading-relaxed">
                                        <span className="font-bold text-[9px] uppercase text-zinc-550 block mb-0.5">
                                          Recommended Containment Action:
                                        </span>
                                        {pred.defensive_recommendation}
                                      </div>
                                    )}
                                  </div>
                                ))
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Chronological Path Continuation */}
                      {latestPrediction.path_continuation && latestPrediction.path_continuation.length > 0 && (
                        <div className="space-y-3 pt-2">
                          <div className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider border-b border-zinc-900 pb-1 flex items-center gap-1.5">
                            <TrendingUp className="h-3.5 w-3.5" />
                            Multi-Step Path Continuation Forecast
                          </div>
                          <div className="flex flex-wrap items-center gap-3 bg-zinc-950/20 border border-zinc-900 rounded p-4 overflow-x-auto">
                            <div className="flex items-center gap-2 bg-zinc-900/50 px-2.5 py-2 border border-zinc-800 rounded">
                              <Activity className="h-3.5 w-3.5 text-zinc-500 shrink-0" />
                              <span className="text-[11px] font-bold text-zinc-300 uppercase">Current Stage</span>
                            </div>

                            {latestPrediction.path_continuation.map((step, idx) => (
                              <React.Fragment key={idx}>
                                <ArrowRight className="h-4.5 w-4.5 text-zinc-700 shrink-0" />
                                <div className="flex flex-col bg-zinc-950 px-3 py-1.5 border border-zinc-900 rounded">
                                  <div className="flex items-center gap-1.5">
                                    <span className="text-[9px] font-bold text-indigo-400 shrink-0 font-mono">
                                      Step {idx + 1}
                                    </span>
                                    <span className="text-[11px] font-bold text-zinc-200 font-mono">{step}</span>
                                  </div>
                                  <span className="text-[10px] text-zinc-400 font-sans font-medium mt-0.5">
                                    {getMitreTitle(step)}
                                  </span>
                                </div>
                              </React.Fragment>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Target entity forecasted */}
                      {latestPrediction.predicted_target && (
                        <div className="space-y-3 pt-2">
                          <div className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider border-b border-zinc-900 pb-1 flex items-center gap-1.5">
                            <Target className="h-3.5 w-3.5" />
                            Forecasted Containment Target
                          </div>
                          <div className="bg-zinc-950/20 border border-zinc-900 rounded p-3 text-[10.5px] text-zinc-400 flex items-center gap-3">
                            <div className="px-2 py-0.5 bg-red-950/20 border border-red-900/40 rounded text-red-400 font-bold uppercase tracking-wider text-[9px]">
                              {latestPrediction.predicted_target.target_type}
                            </div>
                            {latestPrediction.predicted_target.target_entity && (
                              <div className="font-mono text-zinc-300 font-bold bg-zinc-950 px-2 py-1 border border-zinc-900 rounded select-all">
                                {latestPrediction.predicted_target.target_entity}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Historical Prediction Runs table */}
                      <div className="space-y-3 pt-4 border-t border-zinc-900">
                        <div className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider flex items-center gap-1.5">
                          <History className="h-3.5 w-3.5" />
                          Historical Progression Logs
                        </div>
                        {isHistoryLoading ? (
                          <div className="py-8 text-center text-zinc-650 text-xs">
                            Loading history...
                          </div>
                        ) : isHistoryError ? (
                          <div className="py-8 text-center text-red-500 text-xs">
                            Failed to retrieve historical logs.
                          </div>
                        ) : predictionsHistory && predictionsHistory.length > 0 ? (
                          <div className="border border-zinc-900 rounded overflow-hidden bg-zinc-950/20">
                            <Table>
                              <TableHeader className="bg-zinc-950/60">
                                <TableRow className="hover:bg-transparent border-zinc-900">
                                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-44">Run ID</TableHead>
                                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-44">Timestamp</TableHead>
                                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-24">Risk Score</TableHead>
                                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-24">Confidence</TableHead>
                                  <TableHead className="font-mono text-zinc-500 text-[10px] uppercase h-8 w-40">Model</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {predictionsHistory.map((hist) => (
                                  <TableRow key={hist.prediction_id} className="hover:bg-zinc-900/10 border-zinc-900">
                                    <TableCell className="font-mono text-zinc-550 text-[11px] py-2 truncate max-w-[120px]">
                                      {hist.prediction_id}
                                    </TableCell>
                                    <TableCell className="font-mono text-zinc-400 text-[11px] py-2">
                                      {new Date(hist.generated_at).toLocaleString()}
                                    </TableCell>
                                    <TableCell className="font-mono text-zinc-300 text-[11px] py-2 font-bold">
                                      {(hist.escalation_risk_score * 100).toFixed(0)}%
                                    </TableCell>
                                    <TableCell className="py-2">
                                      <span className="text-[9px] uppercase font-mono font-bold text-zinc-400 bg-zinc-950 px-1 border border-zinc-900 rounded">
                                        {hist.confidence}
                                      </span>
                                    </TableCell>
                                    <TableCell className="font-mono text-zinc-500 text-[11px] py-2 truncate max-w-[120px]">
                                      {hist.model_name}
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </div>
                        ) : (
                          <div className="border border-zinc-900 border-dashed rounded p-6 text-center text-zinc-650 text-xs">
                            No historical forecast runs logs computed.
                          </div>
                        )}
                      </div>
                    </div>
                  ) : null}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
