import { fetchApi } from '../api';

export interface PredictionTarget {
  target_type: string;
  target_entity?: string;
}

export interface TechniquePrediction {
  technique_id: string;
  probability?: number;
  score?: number;
  predicted_tactic?: string;
  defensive_recommendation?: string;
}

export interface PredictionResult {
  prediction_id: string;
  incident_id: string;
  generated_at: string;
  valid_until?: string;
  observed_techniques: string[];
  predicted_next_techniques: TechniquePrediction[];
  predicted_target?: PredictionTarget;
  path_continuation: string[];
  escalation_risk_score: number;
  model_name: string;
  model_version: string;
  attack_version: string;
  confidence: string;
  evidence?: string;
  limitations: string;
  trace_id?: string;
  schema_version?: string;
}

export const predictionApi = {
  getLatestPrediction: async (incidentId: string): Promise<PredictionResult> => {
    return fetchApi(`/incidents/${incidentId}/predictions/latest`);
  },

  recomputePrediction: async (incidentId: string): Promise<{ status: string, message: string }> => {
    return fetchApi(`/incidents/${incidentId}/predictions/recompute`, {
      method: 'POST',
    });
  }
};
