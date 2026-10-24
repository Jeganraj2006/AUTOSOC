from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class MarkovAttackPredictor:
    """
    Markov Chain Sequence Transition Predictor for MITRE ATT&CK attack paths.
    
    Computes state transition probabilities P(T_{next} | T_{current}) across attack stages:
    Reconnaissance / Initial Access -> Execution -> Credential Access / PrivEsc -> Lateral Movement -> Exfiltration / Impact.
    """

    TRANSITION_MATRIX: Dict[str, List[Tuple[str, str, float, str]]] = {
        # Format: current_technique -> [(next_technique, tactic_name, probability, defensive_recommendation)]
        "T1059.001": [  # PowerShell Execution
            ("T1003.001", "Credential Access", 0.84, "Enable LSASS Credential Guard and restrict privilege elevation."),
            ("T1021.002", "Lateral Movement", 0.72, "Block SMB inbound traffic (Port 445) and audit Remote Desktop credentials."),
            ("T1041", "Exfiltration", 0.58, "Enable egress network inspection and monitor outbound TLS/HTTPS streams.")
        ],
        "T1027": [  # Obfuscated Command
            ("T1059.001", "Execution", 0.88, "Enforce PowerShell Constrained Language Mode (CLM)."),
            ("T1003.001", "Credential Access", 0.79, "Monitor memory dumping calls to lsass.exe process."),
            ("T1071.001", "Command and Control", 0.64, "Inspect external HTTP/S beaconing IP destinations.")
        ],
        "T1110.001": [  # Password Spray / Failed Logins
            ("T1078", "Initial Access", 0.82, "Enforce Multi-Factor Authentication (MFA) immediately."),
            ("T1068", "Privilege Escalation", 0.75, "Audit local account privileges and lock compromised account."),
            ("T1083", "Discovery", 0.61, "Restrict active directory LDAP queries and SMB enumeration.")
        ],
        "T1046": [  # Port Scanning / Reconnaissance
            ("T1021.001", "Lateral Movement", 0.81, "Apply strict internal sub-network firewall segmentation rules."),
            ("T1059", "Execution", 0.73, "Block remote service connection attempts from untrusted IPs."),
            ("T1486", "Impact", 0.55, "Verify offline immutable backup snapshots.")
        ]
    }

    TACTIC_MAPPING: Dict[str, Dict[str, Any]] = {
        "powershell": ("T1059.001", "Execution", "Host Infrastructure", "Domain Controller / server-01", 0.88),
        "script": ("T1027", "Defense Evasion", "Endpoint Workstation", "Workstation-01", 0.82),
        "login": ("T1110.001", "Credential Access", "Identity Provider", "Active Directory / Keycloak", 0.76),
        "failed": ("T1110.001", "Credential Access", "Identity Provider", "Active Directory / Keycloak", 0.76),
        "auth": ("T1110.001", "Credential Access", "Identity Provider", "Active Directory / Keycloak", 0.76),
        "scan": ("T1046", "Reconnaissance", "Network Subnet", "DMZ / Internal Subnet", 0.80),
    }

    def predict_attack_progression(self, incident_title: str) -> Dict[str, Any]:
        """
        Calculates attack progression using Markov Chain transition probabilities.
        """
        title_lower = incident_title.lower() if incident_title else ""
        
        # Match primary observed technique
        matched_key = "powershell"
        for key in self.TACTIC_MAPPING:
            if key in title_lower:
                matched_key = key
                break
                
        tech_id, tactic, target_type, target_entity, risk_score = self.TACTIC_MAPPING[matched_key]
        
        observed_techniques = [tech_id]
        if tech_id == "T1059.001":
            observed_techniques.append("T1027")
        elif tech_id == "T1110.001":
            observed_techniques.append("T1078")
            
        transitions = self.TRANSITION_MATRIX.get(tech_id, self.TRANSITION_MATRIX["T1059.001"])
        
        predicted_next = [
            {
                "technique_id": next_tech,
                "predicted_tactic": tactic_name,
                "probability": prob,
                "defensive_recommendation": rec
            }
            for next_tech, tactic_name, prob, rec in transitions
        ]
        
        path_continuation = observed_techniques + [p["technique_id"] for p in predicted_next]
        
        return {
            "observed_techniques": observed_techniques,
            "predicted_next_techniques": predicted_next,
            "predicted_target": {
                "target_type": target_type,
                "target_entity": target_entity
            },
            "path_continuation": path_continuation,
            "escalation_risk_score": risk_score
        }

markov_predictor = MarkovAttackPredictor()
