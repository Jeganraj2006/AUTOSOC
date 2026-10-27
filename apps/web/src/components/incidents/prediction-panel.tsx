"use client";

import { BrainCircuit, RefreshCw } from "lucide-react";
import { useLatestPrediction, useRecomputePrediction } from "@/hooks/use-predictions";
import { useMe } from "@/hooks/use-me";
import { canManageTriage } from "@/lib/monitoring";
import { formatTechniqueConfidence, predictionHasModelMetadata } from "@/lib/intelligence";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { OperationalState, RetryButton } from "@/components/ui/operational-state";

export function PredictionPanel({ incidentId }: { incidentId: string }) {
  const { data: currentUser } = useMe();
  const { data: prediction, isLoading, isError, isFetching, refetch } = useLatestPrediction(incidentId);
  const recomputeMutation = useRecomputePrediction();
  const canRecompute = canManageTriage(currentUser);

  const requestRecompute = () => {
    if (!canRecompute) return;
    recomputeMutation.mutate(incidentId);
  };

  if (isLoading) return <Card className="soc-surface border-0"><CardHeader><CardTitle>Attack prediction</CardTitle><CardDescription>Loading the persisted forecast for this incident.</CardDescription></CardHeader></Card>;
  if (isError || !prediction) return <OperationalState kind="error" title="Prediction is unavailable" description="The incident forecast did not return a usable record. Retry the request or request a recompute if your role permits it." action={<div className="flex flex-wrap justify-center gap-2"><RetryButton onClick={() => refetch()} disabled={isFetching} /><Button onClick={requestRecompute} disabled={!canRecompute || recomputeMutation.isPending} variant="outline">Request recompute</Button></div>} />;

  return <Card className="soc-surface gap-0 border-0 py-0"><CardHeader className="flex flex-row items-start justify-between gap-4"><div><CardTitle className="flex items-center gap-2"><BrainCircuit className="size-5 text-primary" />Attack prediction</CardTitle><CardDescription className="mt-1">Persisted model output; predicted behavior is not a confirmed attack.</CardDescription></div><Button variant="outline" size="sm" onClick={requestRecompute} disabled={!canRecompute || recomputeMutation.isPending} title={canRecompute ? undefined : "Your role cannot request prediction recomputation."}><RefreshCw className={`mr-1.5 size-4 ${recomputeMutation.isPending ? "animate-spin" : ""}`} />Recompute</Button></CardHeader><CardContent className="space-y-5"><dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><div><dt className="text-xs text-muted-foreground">Prediction ID</dt><dd className="mt-1 break-all font-mono text-xs text-foreground">{prediction.prediction_id}</dd></div><div><dt className="text-xs text-muted-foreground">Generated</dt><dd className="mt-1 text-sm text-foreground">{new Date(prediction.generated_at).toLocaleString()}</dd></div><div><dt className="text-xs text-muted-foreground">Model</dt><dd className="mt-1 text-sm text-foreground">{predictionHasModelMetadata(prediction.model_name, prediction.model_version) ? `${prediction.model_name} (${prediction.model_version})` : "Not supplied"}</dd></div><div><dt className="text-xs text-muted-foreground">Escalation risk</dt><dd className="mt-1 text-sm text-foreground">{(prediction.escalation_risk_score * 100).toFixed(0)}%</dd></div></dl><div className="grid gap-5 lg:grid-cols-2"><section><h3 className="text-sm font-medium text-foreground">Observed techniques</h3>{prediction.observed_techniques.length ? <ul className="mt-3 flex flex-wrap gap-2">{prediction.observed_techniques.map((technique) => <li key={technique} className="rounded-md border border-border px-2 py-1 font-mono text-xs text-foreground">{technique}</li>)}</ul> : <p className="mt-3 text-sm text-muted-foreground">No observed techniques were supplied.</p>}</section><section><h3 className="text-sm font-medium text-foreground">Predicted next techniques</h3>{prediction.predicted_next_techniques.length ? <ul className="mt-3 space-y-2">{prediction.predicted_next_techniques.map((technique) => <li key={technique.technique_id} className="rounded-md border border-border p-3"><p className="font-mono text-sm text-foreground">{technique.technique_id}</p><p className="mt-1 text-xs text-muted-foreground">{formatTechniqueConfidence(technique.probability, technique.score)}</p>{technique.predicted_tactic ? <p className="mt-1 text-xs text-muted-foreground">Tactic: {technique.predicted_tactic}</p> : null}</li>)}</ul> : <p className="mt-3 text-sm text-muted-foreground">No next-technique candidates were supplied.</p>}</section></div><section className="rounded-lg border border-border p-4"><h3 className="text-sm font-medium text-foreground">Forecast limitations</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">{prediction.limitations || "No model limitations were returned with this prediction."}</p></section>{recomputeMutation.isError ? <p className="text-sm text-destructive">The recompute request failed. No prediction output was changed by this interface.</p> : null}</CardContent></Card>;
}
