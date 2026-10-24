from __future__ import annotations

from typing import Any, Dict, List

from autosoc_api.ml.detector import SecurityAnomalyDetector


class MLDetectionService:
    """
    Service layer connecting security events to the ML detector.
    """

    def __init__(self) -> None:
        self.detector = SecurityAnomalyDetector(
            contamination=0.1,
            random_state=42,
        )

    def train(
        self,
        events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Train the anomaly detection model using security events.
        """

        if len(events) < 2:
            raise ValueError(
                "At least 2 events are required for training."
            )

        self.detector.fit(events)

        return {
            "status": "trained",
            "training_events": len(events),
        }

    def detect(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Run anomaly detection against security events.
        """

        return self.detector.predict(events)

    def train_and_detect(
        self,
        events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Train the model and immediately detect anomalies.
        """

        training_result = self.train(events)
        predictions = self.detect(events)

        anomaly_count = sum(
            1
            for prediction in predictions
            if prediction["is_anomaly"]
        )

        return {
            **training_result,
            "total_events": len(events),
            "anomalies_detected": anomaly_count,
            "normal_events": len(events) - anomaly_count,
            "predictions": predictions,
        }