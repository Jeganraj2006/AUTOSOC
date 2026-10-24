"use client";

import { useEffect, useState } from "react";
import { PredictionResult, predictionApi } from "@/lib/api/predictions";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, RefreshCw, Activity, Zap, Info } from "lucide-react";
import { Button } from "@/components/ui/button";

export function PredictionPanel({ incidentId }: { incidentId: string }) {
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [recomputing, setRecomputing] = useState(false);

  useEffect(() => {
    loadPrediction();
  }, [incidentId]);

  const loadPrediction = async () => {
    setLoading(true);
    try {
      const data = await predictionApi.getLatestPrediction(incidentId);
      setPrediction(data);
      setError("");
    } catch (err: any) {
      if (err.response?.status === 404) {
        // Expected when no prediction exists yet
        setError("No prediction data available yet.");
      } else {
        setError("Failed to load prediction.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRecompute = async () => {
    setRecomputing(true);
    try {
      await predictionApi.recomputePrediction(incidentId);
      // Wait a bit, then reload
      setTimeout(() => loadPrediction(), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setRecomputing(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Attack Progression</CardTitle>
          <CardDescription>Loading forecast...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (error || !prediction) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div className="space-y-1">
            <CardTitle>Attack Progression</CardTitle>
            <CardDescription>{error}</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={handleRecompute} disabled={recomputing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${recomputing ? 'animate-spin' : ''}`} />
            Request Forecast
          </Button>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card className="border-indigo-500/20 bg-indigo-500/5">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <CardTitle className="text-lg font-bold flex items-center text-indigo-400">
            <Zap className="w-5 h-5 mr-2" />
            Attack Progression Forecast
          </CardTitle>
          <CardDescription className="text-xs">
            Model: {prediction.model_name} v{prediction.model_version} • Confidence: {prediction.confidence}
          </CardDescription>
        </div>
        <Button variant="ghost" size="sm" onClick={handleRecompute} disabled={recomputing}>
          <RefreshCw className={`h-4 w-4 ${recomputing ? 'animate-spin' : ''}`} />
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {prediction.predicted_next_techniques.length > 0 ? (
          <div className="space-y-3 mt-4">
            <h4 className="text-sm font-medium text-slate-300">Predicted Next Steps:</h4>
            {prediction.predicted_next_techniques.map((tech, idx) => (
              <div key={idx} className="flex flex-col space-y-1">
                <div className="flex justify-between items-center text-sm">
                  <span className="font-mono text-slate-200">{tech.technique_id}</span>
                  <span className="text-xs text-indigo-300">{Math.round((tech.score || 0))}%</span>
                </div>
                <Progress value={tech.score || 0} className="h-1.5" />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-slate-400 p-4 text-center border border-dashed rounded bg-slate-900/50">
            Insufficient evidence for prediction.
          </div>
        )}

        <div className="flex items-center space-x-2 text-xs text-slate-400 mt-4 p-2 bg-slate-900/50 rounded border border-slate-800">
          <Info className="w-4 h-4 text-slate-500 flex-shrink-0" />
          <p>{prediction.limitations}</p>
        </div>
      </CardContent>
    </Card>
  );
}
