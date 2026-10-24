from typing import List, Dict, Any

class ScoringEngine:
    @staticmethod
    def calculate_risk_score(alerts: List[Dict[str, Any]]) -> float:
        """
        Calculates a blended risk score from multiple alerts.
        For now, uses the max score + a modifier based on count.
        """
        if not alerts:
            return 0.0
            
        max_score = 0.0
        sum_scores = 0.0
        
        for alert in alerts:
            score = 0.0
            # Depending on if it's an ML anomaly or a rule
            if "anomaly_score" in alert and alert["anomaly_score"] is not None:
                score = alert["anomaly_score"] * 100
            elif "hybrid_risk_score" in alert and alert["hybrid_risk_score"] is not None:
                score = alert["hybrid_risk_score"]
            else:
                # Default severity mapping
                sev = alert.get("severity", "low").lower()
                mapping = {"informational": 10, "low": 30, "medium": 60, "high": 85, "critical": 100}
                score = mapping.get(sev, 30)
                
            if score > max_score:
                max_score = score
            sum_scores += score
            
        # Add a small boost for volume, capped at 100
        count_boost = (len(alerts) - 1) * 2.0
        final_score = min(100.0, max_score + count_boost)
        return final_score
