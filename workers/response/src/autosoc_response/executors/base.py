from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from autosoc_response.policy.types import ExecutionMode

class BaseExecutor(ABC):
    """
    Abstract base class for all strict typed response executors.
    NO SHELL/COMMAND executors are permitted here.
    """
    
    def __init__(self, target: str, arguments: Dict[str, Any] = None):
        self.target = target
        self.arguments = arguments or {}

    @abstractmethod
    def validate_target(self) -> Tuple[bool, str]:
        """Validate if the target is in the correct format and permitted."""
        pass

    @abstractmethod
    def dry_run(self) -> Dict[str, Any]:
        """Return the intended actions without modifying any state."""
        pass

    @abstractmethod
    def simulate(self) -> Dict[str, Any]:
        """Simulate the execution and return mocked success."""
        pass

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Perform the actual execution against the connector."""
        pass

    @abstractmethod
    def verify(self) -> Tuple[bool, str]:
        """Verify the state change occurred."""
        pass

    @abstractmethod
    def rollback(self) -> Dict[str, Any]:
        """Rollback the execution if reversible."""
        pass

    def run(self, mode: ExecutionMode) -> Dict[str, Any]:
        """Main entry point to dispatch based on mode."""
        valid, msg = self.validate_target()
        if not valid:
            return {"status": "failed", "reason": f"Target validation failed: {msg}"}
            
        if mode == ExecutionMode.DRY_RUN:
            return {"status": "dry_run", "details": self.dry_run()}
        elif mode == ExecutionMode.SIMULATION:
            return {"status": "simulated", "details": self.simulate()}
        elif mode == ExecutionMode.ANALYST_APPROVED_EXECUTION:
            return {"status": "executed", "details": self.execute()}
        else:
            return {"status": "failed", "reason": f"Unsupported mode: {mode}"}
