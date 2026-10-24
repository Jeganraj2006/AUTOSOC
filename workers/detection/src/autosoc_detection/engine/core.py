import logging
from typing import List, Optional
from autosoc_detection.rules.registry import RuleRegistry
from autosoc_detection.evaluators.predicate import PredicateEvaluator
from autosoc_detection.state.manager import StateManager
from autosoc_detection.alerts.generator import AlertGenerator
from autosoc_schemas.events.normalized import NormalizedSecurityEvent
from autosoc_schemas.events.detection import DetectionResult

logger = logging.getLogger(__name__)

class DetectionEngine:
    def __init__(self, registry: RuleRegistry, state_manager: StateManager):
        self.registry = registry
        self.state_manager = state_manager

    async def evaluate_event(self, event: NormalizedSecurityEvent) -> List[DetectionResult]:
        results = []
        rules = self.registry.get_rules_by_category(event.event_category)
        
        for rule in rules:
            try:
                if not rule.enabled:
                    continue
                    
                is_match = PredicateEvaluator.evaluate(rule.condition, event)
                if not is_match:
                    continue
                    
                # Threshold logic
                if rule.rule_type == "threshold" and rule.threshold:
                    group_vals = []
                    for g in rule.threshold.group_by:
                        val = getattr(event, g, "unknown")
                        group_vals.append(str(val))
                    group_key = ":".join(group_vals)
                    
                    if await self.state_manager.is_suppressed(rule.rule_id, group_key):
                        continue
                        
                    threshold_crossed = await self.state_manager.increment_and_check_threshold(
                        rule.rule_id, group_key, rule.threshold.count, rule.threshold.timeframe
                    )
                    
                    if threshold_crossed:
                        await self.state_manager.set_suppression(
                            rule.rule_id, group_key, rule.threshold.suppression_window
                        )
                        alert = AlertGenerator.generate(rule, event)
                        results.append(alert)
                        
                elif rule.rule_type == "statistical":
                    # For statistical (e.g., new IP seen), we check state
                    # Here we treat rule.threshold.group_by[0] as the category and [1] as field
                    group_key = getattr(event, rule.threshold.group_by[0], "unknown") if rule.threshold and rule.threshold.group_by else "global"
                    val = getattr(event, rule.threshold.group_by[1], "unknown") if rule.threshold and len(rule.threshold.group_by) > 1 else "unknown"
                    
                    is_new = await self.state_manager.check_is_new_value(f"{rule.rule_id}:{group_key}", val, rule.threshold.timeframe if rule.threshold else 86400)
                    if is_new:
                        alert = AlertGenerator.generate(rule, event)
                        results.append(alert)
                
                else: # Match, IOC, Sigma
                    # Simple rule match (Stateless)
                    # Check global rule suppression if configured (for simplicity we use group_key 'global')
                    if await self.state_manager.is_suppressed(rule.rule_id, "global"):
                        continue
                    
                    await self.state_manager.set_suppression(rule.rule_id, "global", rule.threshold.suppression_window if rule.threshold else 300)
                    alert = AlertGenerator.generate(rule, event)
                    results.append(alert)

            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {str(e)}")
                
        return results
