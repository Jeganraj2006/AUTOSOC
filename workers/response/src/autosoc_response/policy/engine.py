from typing import Dict, Any, Tuple
import logging
from datetime import datetime, UTC

from autosoc_response.playbooks.registry import registry
from autosoc_response.policy.types import ActionType, ImpactLevel, ExecutionMode, EnvironmentType

logger = logging.getLogger(__name__)

class PolicyEngine:
    def __init__(self, current_environment: EnvironmentType = EnvironmentType.LAB):
        self.environment = current_environment
        
    def evaluate(self, 
                 action_type: str, 
                 target: str,
                 impact: str,
                 mode: str,
                 approval_status: str,
                 approval_expiration: datetime = None) -> Tuple[bool, str]:
        """
        Evaluate if the execution is permitted.
        Returns (is_allowed, reason)
        """
        # 1. Deny by Default for unknown actions
        try:
            parsed_action = ActionType(action_type)
        except ValueError:
            return False, f"Denied: Unknown action type {action_type}"
            
        try:
            parsed_impact = ImpactLevel(impact)
        except ValueError:
            return False, f"Denied: Unknown impact level {impact}"
            
        # 2. Environment Guard
        if self.environment == EnvironmentType.PRODUCTION:
            return False, "Denied: Production execution is disabled by default in this academic lab."
            
        if parsed_impact == ImpactLevel.CRITICAL and mode != ExecutionMode.SIMULATION:
            return False, "Denied: Critical impact actions are restricted to SIMULATION mode only."
            
        # 3. Target Scope Validation (No wildcards)
        if target in ["*", "0.0.0.0/0", "all", "0.0.0.0"]:
            return False, "Denied: Wildcard or overly broad targets are strictly prohibited."
            
        # 4. Mode and Approval Validation
        if mode == ExecutionMode.ANALYST_APPROVED_EXECUTION:
            if approval_status != "approved":
                return False, f"Denied: Approved execution requires status 'approved', got '{approval_status}'"
                
            if approval_expiration and approval_expiration < datetime.now(UTC):
                return False, "Denied: Approval has expired."
                
        # If it's a dry_run or simulation, we generally allow it if it passed basic checks
        return True, "Allowed by policy."

policy_engine = PolicyEngine(current_environment=EnvironmentType.LAB)
