from typing import Dict, Any

def validate_agent_response(response: str, expected_schema: str = "json") -> bool:
    """
    Validate that the agent response doesn't contain forbidden actions.
    Safety constraint: agents must NOT emit commands to block IPs, disable accounts, etc.
    They must only recommend actions.
    """
    forbidden_terms = ["block ip", "disable user", "shutdown", "isolate host", "rm -rf"]
    
    lower_resp = response.lower()
    for term in forbidden_terms:
        if term in lower_resp:
            return False
            
    return True
