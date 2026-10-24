import numpy as np

def fuse_supervised_outputs(cnn_prob: float, lstm_prob: float, transformer_prob: float) -> float:
    """
    Model Fusion: Weighted supervised fusion.
    For this implementation, we use simple averaging (equal weights), 
    but this can easily be extended to validation-derived weights.
    """
    return (cnn_prob + lstm_prob + transformer_prob) / 3.0

def determine_hybrid_classification(
    known_attack_confidence: float, 
    anomaly_score: float, 
    known_attack_threshold: float = 0.5,
    high_anomaly_threshold: float = 0.8,
    suspicious_anomaly_threshold: float = 0.6,
    risk_context_high: bool = True
) -> str:
    """
    Scientific Guardrail Logic for Phase 11.
    NEVER returns "confirmed zero-day".
    Returns one of: 'normal', 'known_attack', 'suspicious_anomaly', 'potential_zero_day_behavior'.
    """
    # 1. Known Attack Priority
    if known_attack_confidence >= known_attack_threshold:
        return "known_attack"
        
    # 2. Potential Zero Day (High Anomaly + Low Supervised + High Contextual Risk)
    if anomaly_score >= high_anomaly_threshold and risk_context_high:
        return "potential_zero_day_behavior"
        
    # 3. Suspicious Anomaly (Moderate/High Anomaly + Low Supervised, no strong context)
    if anomaly_score >= suspicious_anomaly_threshold:
        return "suspicious_anomaly"
        
    # 4. Normal
    return "normal"
