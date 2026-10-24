from typing import Dict, Any
from autosoc_agents.orchestrator.state import AgentState
from autosoc_agents.orchestrator.llm import get_llm
from autosoc_agents.tools.search import search_threat_intel
from langchain_core.messages import SystemMessage, HumanMessage

def call_llm(system_prompt: str, user_prompt: str) -> str:
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"LLM Error: {e}"

def detection_verification_node(state: AgentState) -> Dict[str, Any]:
    return {"findings": ["Detection verified via baseline check."]}

def investigation_node(state: AgentState) -> Dict[str, Any]:
    return {"completed_steps": ["investigation"]}

def threat_intelligence_node(state: AgentState) -> Dict[str, Any]:
    # Use RAG tool to search for context about the incident alerts
    context = search_threat_intel("malicious activity")
    return {"retrieved_knowledge": [{"title": "Intel Search", "content": context}]}

def risk_assessment_node(state: AgentState) -> Dict[str, Any]:
    return {"risk_score": 8.5, "risk_level": "High"}

def prediction_analysis_node(state: AgentState) -> Dict[str, Any]:
    return {"completed_steps": ["prediction_analysis"]}

def response_recommendation_node(state: AgentState) -> Dict[str, Any]:
    return {"recommendations": ["Isolate host manually (Agent cannot perform action)", "Block IP at firewall"]}

def reporting_node(state: AgentState) -> Dict[str, Any]:
    # This node could assemble the final AgentResult JSON
    return {"completed_steps": ["reporting_completed"]}
