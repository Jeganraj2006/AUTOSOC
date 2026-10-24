import os
import yaml
import logging
from typing import Dict, List
from .rule_models import CorrelationRule

logger = logging.getLogger(__name__)

class RuleRegistry:
    def __init__(self, rules_dir: str):
        self.rules_dir = rules_dir
        self.rules: Dict[str, CorrelationRule] = {}
        self.load_rules()

    def load_rules(self):
        self.rules.clear()
        if not os.path.exists(self.rules_dir):
            logger.warning(f"Rules directory {self.rules_dir} not found.")
            return
            
        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(self.rules_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                        rule = CorrelationRule(**data)
                        self.rules[rule.id] = rule
                except Exception as e:
                    logger.error(f"Failed to load rule {filename}: {e}")
                    
        logger.info(f"Loaded {len(self.rules)} correlation rules.")

    def get_rule(self, rule_id: str) -> CorrelationRule:
        return self.rules.get(rule_id)
        
    def get_all_rules(self) -> List[CorrelationRule]:
        return list(self.rules.values())

rules_dir = os.environ.get("CORRELATION_RULES_DIR", "../../../.agents/rules/correlation")
registry = RuleRegistry(rules_dir)
