import logging
import uuid
from datetime import datetime
from autosoc_schemas.events.detection import DetectionResult
from autosoc_correlation.rules.registry import registry
from autosoc_correlation.state.redis_manager import state_manager
from autosoc_correlation.scoring.engine import ScoringEngine
from autosoc_correlation.incidents.manager import IncidentManager

logger = logging.getLogger(__name__)

async def correlate_alert(alert: DetectionResult):
    """
    Evaluates an incoming alert against all active correlation rules.
    If conditions are met, creates or updates an incident.
    """
    alert_dict = alert.model_dump(mode='json')
    rules = registry.get_all_rules()
    
    for rule in rules:
        # Extract entities from alert
        entities_present = extract_entities(alert_dict)
        
        # Check if alert matches required entities for this rule
        for req_entity in rule.required_entities:
            # E.g. "source_ip"
            # We look for any entity where role matches or the key exists
            entity_vals = [e['value'] for e in entities_present if e.get('role') == req_entity]
            
            for entity_val in entity_vals:
                # Add to state tracking
                state_manager.add_alert(
                    entity_id=entity_val, 
                    rule_id=rule.id, 
                    alert_data=alert_dict, 
                    window_seconds=rule.time_window_seconds
                )
                
                # Retrieve updated alert bucket
                correlated_alerts = state_manager.get_alerts(entity_id=entity_val, rule_id=rule.id)
                
                if len(correlated_alerts) >= rule.trigger_threshold:
                    # Threshold met! Check if active incident exists
                    active_incident_id = state_manager.get_active_incident(entity_id=entity_val, rule_id=rule.id)
                    
                    # Calculate new risk score
                    new_score = ScoringEngine.calculate_risk_score(correlated_alerts)
                    
                    if active_incident_id:
                        # Update existing incident
                        await IncidentManager.update_incident(
                            incident_id=active_incident_id,
                            alerts=correlated_alerts,
                            new_score=new_score,
                            rule=rule
                        )
                    else:
                        # Create new incident
                        new_incident_id = str(uuid.uuid4())
                        await IncidentManager.create_incident(
                            incident_id=new_incident_id,
                            alerts=correlated_alerts,
                            entity_id=entity_val,
                            new_score=new_score,
                            rule=rule
                        )
                        state_manager.set_active_incident(entity_id=entity_val, rule_id=rule.id, incident_id=new_incident_id)

def extract_entities(alert: dict) -> list:
    """Extract entities from alert structure"""
    entities = alert.get("entities", [])
    return entities
