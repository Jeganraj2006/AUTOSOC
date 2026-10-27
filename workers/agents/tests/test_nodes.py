from autosoc_agents.agents import nodes


def state():
    return {
        "incident_id": "incident-1",
        "execution_id": "execution-1",
        "incident_data": {"severity": "high", "primary_entities": ["198.51.100.10"], "candidate_mitre_references": ["T1110"], "predictions": [{"technique_id": "T1021"}]},
        "alerts_data": [{"id": "alert-1", "title": "Failed logins", "severity": "high"}],
        "events_data": [{"id": "event-1"}],
        "findings": [], "errors": [], "completed_steps": [], "retrieved_knowledge": [], "recommendations": [], "node_responses": {},
    }


def test_each_deterministic_node_preserves_evidence_or_explicitly_limits_actions():
    s = state()
    assert nodes.detection_verification_node(s)["evidence_citations"] == ["alert:alert-1"]
    assert nodes.investigation_node(s)["node_responses"]["investigation"]["observed_entities"] == ["198.51.100.10"]
    assert nodes.threat_intelligence_node(s)["node_responses"]["threat_intelligence"]["external_lookup"] is False
    assert nodes.risk_assessment_node(s)["risk_score"] == 7.0
    assert nodes.prediction_analysis_node(s)["node_responses"]["prediction_analysis"]["prediction_count"] == 1
    assert nodes.response_recommendation_node(s)["recommendations"] == []
    assert nodes.reporting_node(s)["node_responses"]["reporting"]["findings_count"] == 0
