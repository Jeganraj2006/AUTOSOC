import re
from typing import Any
from autosoc_detection.rules.models import RuleCondition
from autosoc_schemas.events.normalized import NormalizedSecurityEvent

class PredicateEvaluator:
    @staticmethod
    def evaluate(condition: RuleCondition, event: NormalizedSecurityEvent) -> bool:
        if condition.AND:
            return all(PredicateEvaluator.evaluate(c, event) for c in condition.AND)
        if condition.OR:
            return any(PredicateEvaluator.evaluate(c, event) for c in condition.OR)
        if condition.NOT:
            return not PredicateEvaluator.evaluate(condition.NOT, event)
            
        if not condition.field:
            return False
            
        # Get field value from event using dict representation
        event_dict = event.model_dump(exclude_none=True)
        
        # Support dot notation for nested fields
        field_parts = condition.field.split('.')
        current_val = event_dict
        for part in field_parts:
            if isinstance(current_val, dict) and part in current_val:
                current_val = current_val[part]
            else:
                current_val = None
                break
                
        # Evaluate operator
        op = condition.operator
        val = condition.value
        
        if op == "exists":
            return current_val is not None
        if op == "not_exists":
            return current_val is None
            
        if current_val is None:
            return False
            
        if op == "equals":
            # For exact match, ensure we are comparing against same type where possible
            if isinstance(current_val, list):
                return val in current_val
            return str(current_val).lower() == str(val).lower() if isinstance(val, str) else current_val == val
            
        if op == "contains":
            if isinstance(current_val, (str, list)):
                return str(val).lower() in (str(v).lower() for v in current_val) if isinstance(current_val, list) else str(val).lower() in str(current_val).lower()
            return False
            
        if op == "startswith":
            return str(current_val).lower().startswith(str(val).lower())
            
        if op == "endswith":
            return str(current_val).lower().endswith(str(val).lower())
            
        if op == "regex":
            try:
                # Compile regex with size limit implied by safe practices, but we just use python re
                pattern = re.compile(str(val), re.IGNORECASE)
                return bool(pattern.search(str(current_val)))
            except re.error:
                return False
                
        if op == "in":
            if not isinstance(val, list):
                return False
            if isinstance(current_val, list):
                # Any element in current_val in val list
                return any(str(c).lower() in (str(v).lower() for v in val) for c in current_val)
            return str(current_val).lower() in (str(v).lower() for v in val)
            
        if op == "not_in":
            if not isinstance(val, list):
                return False
            return str(current_val).lower() not in (str(v).lower() for v in val)

        return False
