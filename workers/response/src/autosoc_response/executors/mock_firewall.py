from typing import Dict, Any, Tuple
from autosoc_response.executors.base import BaseExecutor

class MockFirewallExecutor(BaseExecutor):
    """
    Simulates blocking an IP on a mock firewall. 
    Can persist to a local test mock if needed.
    """
    
    def validate_target(self) -> Tuple[bool, str]:
        import ipaddress
        try:
            ipaddress.ip_address(self.target)
            # Ensure it's not a local broadcast/loopback unless it's a test IP
            if self.target == "127.0.0.1":
                return False, "Cannot block localhost"
            return True, "Valid IP"
        except ValueError:
            return False, "Target must be a valid IP address"

    def dry_run(self) -> Dict[str, Any]:
        return {
            "intended_action": "block_ip",
            "target": self.target,
            "expected_impact": "Loss of network connectivity from target IP",
            "rollback_plan": "Unblock IP from mock firewall"
        }

    def simulate(self) -> Dict[str, Any]:
        return {
            "action": "block_ip",
            "target": self.target,
            "status": "SIMULATED_SUCCESS",
            "message": f"Successfully simulated blocking {self.target} on mock firewall"
        }

    def execute(self) -> Dict[str, Any]:
        # MVP: the 'real' execution in lab mode is just writing to a mocked state file or returning success.
        # We will treat this exactly like simulate since it's an academic lab, but log it as 'executed'.
        print(f"LAB EXECUTION: Blocking IP {self.target} on mock firewall.")
        return {
            "action": "block_ip",
            "target": self.target,
            "status": "SUCCESS",
            "message": f"Successfully blocked {self.target} on mock firewall"
        }

    def verify(self) -> Tuple[bool, str]:
        return True, "Mock firewall reports IP is blocked."

    def rollback(self) -> Dict[str, Any]:
        print(f"LAB ROLLBACK: Unblocking IP {self.target} on mock firewall.")
        return {
            "action": "unblock_ip",
            "target": self.target,
            "status": "SUCCESS",
            "message": f"Successfully unblocked {self.target}"
        }
