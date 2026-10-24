from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import IsolationForest

from autosoc_api.ml.features import FEATURE_COLUMNS, events_to_dataframe


class SecurityAnomalyDetector:
    """
    Isolation Forest based anomaly detector for security events.

    The model learns the general distribution of the supplied security
    events and identifies events that significantly differ from it.
    """

    def __init__(
        self,
        contamination: float = 0.2,
        random_state: int = 42,
    ) -> None:
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )

        self.is_fitted = False

    def fit(self, events: List[Dict[str, Any]]) -> None:
        """
        Train the anomaly detector using security events.
        """

        dataframe = events_to_dataframe(events)

        if len(dataframe) < 2:
            raise ValueError(
                "At least 2 security events are required to train the model."
            )

        self.model.fit(dataframe[FEATURE_COLUMNS])

        self.is_fitted = True

    def predict(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict whether each event is normal or anomalous.
        """

        if not self.is_fitted:
            raise RuntimeError(
                "The anomaly detector must be fitted before prediction."
            )

        if not events:
            return []

        dataframe = events_to_dataframe(events)

        features = dataframe[FEATURE_COLUMNS]

        predictions = self.model.predict(features)

        decision_scores = self.model.decision_function(features)

        results: List[Dict[str, Any]] = []

        for event, prediction, decision_score in zip(
            events,
            predictions,
            decision_scores,
        ):
            # Isolation Forest: 1 = normal, -1 = anomaly
            is_anomaly = prediction == -1
            anomaly_score = self._calculate_anomaly_score(float(decision_score))

            # Domain heuristics for security threat categories & failed outcomes
            cat = str(event.get("event_category", "")).lower()
            evt_type = str(event.get("event_type", "")).lower()
            outcome = str(event.get("event_outcome", "")).lower()
            msg = str(event.get("message", "")).lower()

            if (
                "lsass" in evt_type or "mimikatz" in msg or
                "powershell" in evt_type or "-enc" in msg or
                "exfiltration" in cat or "http_post" in evt_type or
                "smb_exec" in evt_type or "psexec" in msg or
                "credential" in cat or "lateral" in cat or
                outcome in ["failure", "failed"]
            ):
                is_anomaly = True
                anomaly_score = max(anomaly_score, 88.5)

            results.append(
                {
                    "event_id": str(event.get("normalized_event_id") or event.get("event_id")),
                    "is_anomaly": bool(is_anomaly),
                    "anomaly_score": anomaly_score,
                    "model_score": round(float(decision_score), 6),
                }
            )

        return results

    @staticmethod
    def _calculate_anomaly_score(decision_score: float) -> float:
        """
        Convert Isolation Forest's decision score into a 0-100
        anomaly score.

        Higher value = more anomalous.
        """

        # Isolation Forest normally produces scores roughly around
        # the range [-0.5, 0.5].
        normalized = 0.5 - decision_score

        score = normalized * 100.0

        return round(
            float(np.clip(score, 0.0, 100.0)),
            2,
        )