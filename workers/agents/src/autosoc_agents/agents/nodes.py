"""Deterministic, evidence-preserving stages for the legacy worker graph.

These are graph nodes, not independent LLM agents. Local-model inference is
performed by the incident worker and is persisted separately with its evidence.
"""

from typing import Any, Dict

from autosoc_agents.orchestrator.state import AgentState


def _alerts(state: AgentState) -> list[dict[str, Any]]:
    return [alert for alert in state.get("alerts_data", []) if isinstance(alert, dict)]


def detection_verification_node(state: AgentState) -> Dict[str, Any]:
    alerts = _alerts(state)
    citations = [f"alert:{alert.get('id') or alert.get('alert_id')}" for alert in alerts if alert.get("id") or alert.get("alert_id")]
    findings = [
        f"Observed persisted alert: {alert.get('title', 'untitled')} ({alert.get('severity', 'unknown')})."
        for alert in alerts
    ]
    return {
        "completed_steps": ["detection_verification"],
        "findings": findings,
        "evidence_citations": citations,
        "node_responses": {"detection_verification": {"alert_count": len(alerts), "evidence_citations": citations}},
    }


def investigation_node(state: AgentState) -> Dict[str, Any]:
    entities = state.get("incident_data", {}).get("primary_entities", [])
    return {
        "completed_steps": ["investigation"],
        "node_responses": {"investigation": {"observed_entities": entities, "event_count": len(state.get("events_data", []))}},
    }


def threat_intelligence_node(state: AgentState) -> Dict[str, Any]:
    # No external lookup is implied by this stage. It surfaces only references
    # already attached to the incident by correlation/detection.
    techniques = state.get("incident_data", {}).get("candidate_mitre_references", [])
    return {
        "completed_steps": ["threat_intelligence"],
        "retrieved_knowledge": [{"title": "Persisted ATT&CK candidates", "content": ", ".join(map(str, techniques)), "provenance": "incident.candidate_mitre_references"}],
        "node_responses": {"threat_intelligence": {"external_lookup": False, "techniques": techniques}},
    }


def risk_assessment_node(state: AgentState) -> Dict[str, Any]:
    severity = str(state.get("incident_data", {}).get("severity", "unknown")).lower()
    score_by_severity = {"critical": 9.0, "high": 7.0, "medium": 5.0, "low": 3.0, "informational": 1.0}
    score = score_by_severity.get(severity, 0.0)
    return {
        "completed_steps": ["risk_assessment"],
        "risk_score": score,
        "risk_level": severity,
        "node_responses": {"risk_assessment": {"method": "deterministic severity mapping", "score": score}},
    }


def prediction_analysis_node(state: AgentState) -> Dict[str, Any]:
    predictions = state.get("incident_data", {}).get("predictions", [])
    return {
        "completed_steps": ["prediction_analysis"],
        "node_responses": {"prediction_analysis": {"prediction_count": len(predictions), "provenance": "persisted predictions"}},
    }


def response_recommendation_node(state: AgentState) -> Dict[str, Any]:
    # This graph cannot create, approve, or execute a response. Proposals must
    # be explicit immutable records through the RBAC-protected API.
    return {
        "completed_steps": ["response_recommendation"],
        "recommendations": [],
        "node_responses": {"response_recommendation": {"automatic_actions": False, "proposal_required": True}},
    }


def reporting_node(state: AgentState) -> Dict[str, Any]:
    return {
        "completed_steps": ["reporting"],
        "node_responses": {"reporting": {"findings_count": len(state.get("findings", [])), "errors": state.get("errors", [])}},
    }
