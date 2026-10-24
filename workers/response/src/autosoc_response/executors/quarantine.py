import os
import hashlib
import shutil
from typing import Dict, Any, Tuple
from autosoc_response.executors.base import BaseExecutor

# For lab test purposes only
QUARANTINE_ROOT = "/tmp/lab/quarantine-test"

class FileQuarantineExecutor(BaseExecutor):
    """
    Quarantines a file by moving it to a controlled test directory.
    """
    
    def validate_target(self) -> Tuple[bool, str]:
        # Disallow directory traversal
        if ".." in self.target or not self.target.startswith("/tmp/lab/test-malware"):
            return False, "Target file must be within /tmp/lab/test-malware for academic safety"
        if not os.path.exists(self.target):
            # Since this might be a simulation, we allow it to pass validation if file doesn't exist?
            # Actually, let's just log a warning but pass validation so simulation can run
            pass
        return True, "Valid test file path"

    def dry_run(self) -> Dict[str, Any]:
        return {
            "intended_action": "quarantine_file",
            "target": self.target,
            "expected_impact": f"File {self.target} moved to {QUARANTINE_ROOT}",
            "rollback_plan": "Restore file to original location"
        }

    def simulate(self) -> Dict[str, Any]:
        return {
            "action": "quarantine_file",
            "target": self.target,
            "status": "SIMULATED_SUCCESS",
            "message": f"Successfully simulated quarantining {self.target}"
        }

    def execute(self) -> Dict[str, Any]:
        os.makedirs(QUARANTINE_ROOT, exist_ok=True)
        if not os.path.exists(self.target):
            return {"status": "FAILED", "reason": "File does not exist"}
            
        filename = os.path.basename(self.target)
        dest = os.path.join(QUARANTINE_ROOT, filename)
        
        # Calculate hash for evidence
        sha256 = hashlib.sha256()
        with open(self.target, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
                
        hash_val = sha256.hexdigest()
        shutil.move(self.target, dest)
        
        # Save original path for rollback
        self.arguments["original_path"] = self.target
        self.arguments["quarantine_path"] = dest
        
        return {
            "action": "quarantine_file",
            "target": self.target,
            "status": "SUCCESS",
            "message": f"Quarantined to {dest}. Hash: {hash_val}"
        }

    def verify(self) -> Tuple[bool, str]:
        dest = self.arguments.get("quarantine_path")
        if dest and os.path.exists(dest) and not os.path.exists(self.target):
            return True, "File successfully quarantined"
        return False, "Verification failed, file may still exist at original path"

    def rollback(self) -> Dict[str, Any]:
        dest = self.arguments.get("quarantine_path")
        if not dest or not os.path.exists(dest):
            return {"status": "FAILED", "reason": "Quarantined file not found for rollback"}
            
        shutil.move(dest, self.target)
        return {
            "action": "restore_file",
            "target": self.target,
            "status": "SUCCESS",
            "message": "File restored to original path"
        }
