from typing import Dict, Any, Tuple
from autosoc_response.executors.base import BaseExecutor

class KeycloakDisableExecutor(BaseExecutor):
    """
    Simulates disabling an account in Keycloak test realm.
    """
    def validate_target(self) -> Tuple[bool, str]:
        # Basic validation: ensure it's not the admin or current user
        if self.target.lower() in ["admin", "system", "autosoc-service"]:
            return False, "Cannot disable system or administrator accounts"
        return True, "Valid test user"

    def dry_run(self) -> Dict[str, Any]:
        return {
            "intended_action": "disable_account",
            "target": self.target,
            "expected_impact": "User cannot login to test realm",
            "rollback_plan": "Re-enable user account in Keycloak"
        }

    def simulate(self) -> Dict[str, Any]:
        return {
            "action": "disable_account",
            "target": self.target,
            "status": "SIMULATED_SUCCESS",
            "message": f"Successfully simulated disabling {self.target}"
        }

    def execute(self) -> Dict[str, Any]:
        print(f"LAB EXECUTION: Disabling account {self.target} in Keycloak mock.")
        return {
            "action": "disable_account",
            "target": self.target,
            "status": "SUCCESS",
            "message": f"Successfully disabled {self.target}"
        }

    def verify(self) -> Tuple[bool, str]:
        return True, "Keycloak mock reports user is disabled."

    def rollback(self) -> Dict[str, Any]:
        print(f"LAB ROLLBACK: Re-enabling account {self.target}.")
        return {
            "action": "enable_account",
            "target": self.target,
            "status": "SUCCESS",
            "message": f"Successfully re-enabled {self.target}"
        }
