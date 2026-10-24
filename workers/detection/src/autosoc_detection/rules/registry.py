import yaml
import os
import logging
from typing import Dict, List, Optional
from autosoc_detection.rules.models import RuleModel
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class RuleRegistry:
    def __init__(self, rules_dir: str):
        self.rules_dir = rules_dir
        self.rules: Dict[str, RuleModel] = {}
        self.invalid_rules: List[Dict[str, str]] = []

    def load_rules(self) -> None:
        """Scan rules_dir and load all .yaml files."""
        self.rules.clear()
        self.invalid_rules.clear()
        
        if not os.path.exists(self.rules_dir):
            logger.warning(f"Rules directory {self.rules_dir} does not exist.")
            return

        for root, _, files in os.walk(self.rules_dir):
            for file in files:
                if file.endswith(('.yml', '.yaml')):
                    self._load_file(os.path.join(root, file))
                    
        logger.info(f"Loaded {len(self.rules)} active rules. Found {len(self.invalid_rules)} invalid rules.")

    def _load_file(self, filepath: str) -> None:
        try:
            with open(filepath, 'r') as f:
                content = yaml.safe_load(f)
                
            if not content:
                return

            if isinstance(content, dict):
                self._parse_rule(content, filepath)
            elif isinstance(content, list):
                for item in content:
                    self._parse_rule(item, filepath)
                    
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {str(e)}")
            self.invalid_rules.append({"filepath": filepath, "error": str(e)})

    def _parse_rule(self, raw: dict, filepath: str) -> None:
        try:
            # Handle minimal Sigma subset structure mapping if applicable
            if "logsource" in raw and "detection" in raw:
                # Sigma rule detected, we'd theoretically convert it here.
                # For Phase 9 strict boundary, we only map the sigma subset to RuleModel if possible.
                # Simplified approach for this task: parse as autosoc rule format directly
                # If it's pure Sigma, we rely on a pre-parser or Sigma integration to map it.
                pass
                
            rule = RuleModel(**raw)
            if rule.rule_id in self.rules:
                logger.warning(f"Duplicate rule ID found: {rule.rule_id} in {filepath}")
                self.invalid_rules.append({"filepath": filepath, "error": f"Duplicate rule ID: {rule.rule_id}"})
                return
                
            if rule.enabled:
                self.rules[rule.rule_id] = rule
                
        except ValidationError as e:
            logger.error(f"Validation failed for rule in {filepath}: {e.errors()}")
            self.invalid_rules.append({"filepath": filepath, "error": str(e.errors())})

    def get_all_rules(self) -> List[RuleModel]:
        return list(self.rules.values())

    def get_rules_by_category(self, category: str) -> List[RuleModel]:
        return [r for r in self.rules.values() if not r.event_categories or category in r.event_categories]
