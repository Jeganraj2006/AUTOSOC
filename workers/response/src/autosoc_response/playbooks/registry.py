import os
import yaml
import logging
from typing import Dict, List, Optional
from autosoc_response.playbooks.schema import ResponsePlaybook

logger = logging.getLogger(__name__)

class PlaybookRegistry:
    def __init__(self, registry_dir: str):
        self.registry_dir = registry_dir
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.load_playbooks()
        
    def load_playbooks(self):
        self.playbooks.clear()
        if not os.path.exists(self.registry_dir):
            logger.warning(f"Playbook registry directory not found: {self.registry_dir}")
            return
            
        for root, _, files in os.walk(self.registry_dir):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    path = os.path.join(root, file)
                    self._load_file(path)
                    
    def _load_file(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                
            playbook = ResponsePlaybook(**data)
            
            if playbook.playbook_id in self.playbooks:
                logger.error(f"Duplicate playbook ID detected: {playbook.playbook_id}. Skipping {filepath}")
                return
                
            # strict validation checks (shell safety)
            if self._contains_unsafe_shell(data):
                logger.error(f"Unsafe shell/command fragments detected in {filepath}. Skipping.")
                return
                
            self.playbooks[playbook.playbook_id] = playbook
            logger.info(f"Loaded playbook: {playbook.playbook_id} (v{playbook.version})")
        except Exception as e:
            logger.error(f"Failed to load playbook {filepath}: {e}")
            
    def _contains_unsafe_shell(self, data: dict) -> bool:
        # Recursive check for forbidden keywords in values
        import re
        forbidden = [r"\bsh\b", r"\bbash\b", r"\bpowershell\b", r"\bcmd\.exe\b", r"\beval\b", r"\bexec\s+\b"]
        
        def _check(obj):
            if isinstance(obj, str):
                lower = obj.lower()
                return any(re.search(f, lower) for f in forbidden)
            if isinstance(obj, dict):
                return any(_check(v) for v in obj.values())
            if isinstance(obj, list):
                return any(_check(item) for item in obj)
            return False
            
        return _check(data)
        
    def get(self, playbook_id: str) -> Optional[ResponsePlaybook]:
        return self.playbooks.get(playbook_id)
        
    def list_all(self) -> List[ResponsePlaybook]:
        return list(self.playbooks.values())

# Singleton instance initialized with the correct path
import pathlib
base_dir = pathlib.Path(__file__).parent.parent.parent.parent.parent.parent
default_playbook_dir = base_dir / "rules" / "response-playbooks"

registry = PlaybookRegistry(str(default_playbook_dir))
