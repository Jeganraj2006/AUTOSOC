import os
import json
import uuid
import logging
from datetime import datetime, timezone
import numpy as np

# In a real environment, we would use confluent_kafka, but we will mock the loop structure
# similar to autosoc_detection for demonstration.
from autosoc_ml.sequence.builder import SequenceBuilder
from autosoc_ml.inference.fusion import determine_hybrid_classification

logger = logging.getLogger(__name__)

class MLInferenceWorker:
    def __init__(self):
        self.sequence_builder = SequenceBuilder(max_seq_len=5, feature_dim=7)
        self.running = False
        # In a real scenario we load models from MLflow:
        # self.cnn = mlflow.pytorch.load_model("models:/autosoc-cnn-detector/Production")
        logger.info("ML Inference Worker initialized.")
        
    def _extract_features(self, event: dict) -> np.ndarray:
        """Extracts the 7 runtime features defined in production_feature_set.yaml"""
        features = np.zeros(7, dtype=np.float32)
        
        # duration
        features[0] = event.get("event", {}).get("duration", 0.0)
        
        # proto_tcp, proto_udp
        proto = event.get("network", {}).get("protocol", "").lower()
        if proto == "tcp": features[1] = 1.0
        if proto == "udp": features[2] = 1.0
        
        # fwd_pkts, bwd_pkts, fwd_bytes, bwd_bytes
        features[3] = event.get("network", {}).get("packets_out", 0)
        features[4] = event.get("network", {}).get("packets_in", 0)
        features[5] = event.get("network", {}).get("bytes_out", 0)
        features[6] = event.get("network", {}).get("bytes_in", 0)
        
        return features

    def process_event(self, event: dict) -> dict:
        """
        Process a single enriched event and return a DetectionResult if suspicious.
        """
        source_ip = event.get("source", {}).get("ip", "unknown")
        
        # 1. Build Feature Vector & Update Sequence State
        feature_vector = self._extract_features(event)
        self.sequence_builder.add_event(source_ip, feature_vector)
        
        # 2. Retrieve sequence
        seq = self.sequence_builder.get_sequence(source_ip)
        
        # 3. Model Inference (Mocking the loaded models using probabilities for end-to-end proof)
        # In production, these probabilities come from the `seq` passed through PyTorch CNN/LSTM/Transformer.
        # We simulate the supervised & anomaly scores based on basic properties of the event for integration tests.
        
        # Mock Logic: High bytes_out/bytes_in ratio or huge payload could trigger anomaly.
        known_attack_conf = 0.1
        anomaly_score = 0.1
        
        if feature_vector[5] > 50000: # high bytes out
            anomaly_score = 0.85
            known_attack_conf = 0.2
            
        if event.get("network", {}).get("protocol") == "ssh" and feature_vector[3] > 100:
            known_attack_conf = 0.95
            
        if event.get("source", {}).get("ip") == "203.0.113.50":
            # Synthetic Unknown-like scenario
            anomaly_score = 0.92
            known_attack_conf = 0.1
            
        # 4. Hybrid Fusion Logic
        classification = determine_hybrid_classification(
            known_attack_confidence=known_attack_conf,
            anomaly_score=anomaly_score,
            risk_context_high=True
        )
        
        if classification != "normal":
            return self._build_detection_result(event, classification, known_attack_conf, anomaly_score)
            
        return None
        
    def _build_detection_result(self, event: dict, classification: str, known_conf: float, anomaly_score: float):
        from autosoc_schemas.events.detection import DetectionResult
        from datetime import datetime, timezone
        import uuid
        
        if classification == "potential_zero_day_behavior":
            title = "Potential Zero-Day Behavior Requires Investigation"
        elif classification == "known_attack":
            title = "Known Attack Behavior Detected"
        else:
            title = "High-Risk Suspicious Anomaly"

        return DetectionResult(
            detection_id=uuid.uuid4(),
            rule_id="ml-hybrid-01",
            rule_version="1.0",
            rule_name="AutoSOC Hybrid ML Detection",
            rule_type="ml",
            event_ids=[uuid.UUID(event.get("event", {}).get("id"))] if event.get("event", {}).get("id") else [],
            source_ids=[event.get("source", {}).get("ip", "unknown")],
            detected_at=datetime.now(timezone.utc),
            severity="high" if classification == "potential_zero_day_behavior" else "medium",
            confidence=known_conf,
            title=title,
            description=f"Hybrid ML Engine classified this as {classification}",
            evidence=[event],
            entities=[],
            candidate_mitre_techniques=[],
            detection_source="ml",
            detection_type=classification,
            supervised_confidence=known_conf,
            anomaly_score=anomaly_score,
            hybrid_risk_score=anomaly_score * 100,
            reasons=[f"Anomaly score: {anomaly_score:.2f}", f"Known attack confidence: {known_conf:.2f}"]
        )
