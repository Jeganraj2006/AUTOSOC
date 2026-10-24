import os
import json

from autosoc_ml.progression.models.markov import MarkovProgressionPredictor
from autosoc_ml.progression.features.builder import ProgressionFeatureBuilder


class ProgressionService:
    def __init__(self, model_path: str, vocab_path: str):
        self.builder = ProgressionFeatureBuilder(vocab_path)
        self.model = MarkovProgressionPredictor()

        # Load trained Markov model
        if os.path.exists(model_path):
            with open(model_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.model.transition_counts.update(data.get("transition_counts", {}))
            self.model.state_totals.update(data.get("state_totals", {}))
            self.model.global_prior.update(data.get("global_prior", {}))

            print(f"Loaded trained Markov model from {model_path}")
        else:
            print(f"WARNING: Model file not found: {model_path}")

    def predict(self, incident_mappings: list) -> dict:
        sequence = self.builder.extract_sequence(incident_mappings)

        if not sequence:
            return {
                "predictions": [],
                "observed": []
            }

        current_tech = sequence[-1]

        top_k = self.model.predict(current_tech, top_k=3)

        predictions = []

        for tech, prob in top_k:
            predictions.append({
                "technique_id": tech,
                "probability": float(prob),
                "score": float(prob) * 100
            })

        return {
            "predictions": predictions,
            "observed": sequence
        }