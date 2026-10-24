from langgraph.graph import StateGraph, END
from autosoc_agents.orchestrator.state import AgentState
from autosoc_agents.agents.nodes import (
    detection_verification_node,
    investigation_node,
    threat_intelligence_node,
    risk_assessment_node,
    prediction_analysis_node,
    response_recommendation_node,
    reporting_node
)

def build_investigation_graph():
    """
    Builds the LangGraph state machine for the full incident investigation workflow.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("detection_verification", detection_verification_node)
    workflow.add_node("investigation", investigation_node)
    workflow.add_node("threat_intelligence", threat_intelligence_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("prediction_analysis", prediction_analysis_node)
    workflow.add_node("response_recommendation", response_recommendation_node)
    workflow.add_node("reporting", reporting_node)
    
    # Define edges (Linear pipeline for now, can be conditional later)
    workflow.set_entry_point("detection_verification")
    
    workflow.add_edge("detection_verification", "investigation")
    workflow.add_edge("investigation", "threat_intelligence")
    workflow.add_edge("threat_intelligence", "risk_assessment")
    workflow.add_edge("risk_assessment", "prediction_analysis")
    workflow.add_edge("prediction_analysis", "response_recommendation")
    workflow.add_edge("response_recommendation", "reporting")
    
    workflow.add_edge("reporting", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app
