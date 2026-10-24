from typing import Annotated, Dict, List, Any, Optional, TypedDict
import operator

# Reducer functions
def merge_list(a: List[str], b: List[str]) -> List[str]:
    return a + b

def merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return {**a, **b}

class AgentState(TypedDict):
    """
    The state of the agent investigation workflow.
    LangGraph will pass this state between nodes.
    """
    # Core Identity
    incident_id: str
    execution_id: str
    
    # Input/Context Data
    incident_data: Dict[str, Any]
    alerts_data: List[Dict[str, Any]]
    events_data: List[Dict[str, Any]]
    
    # Internal Reasoning State
    current_step: str
    investigation_plan: List[str]
    completed_steps: Annotated[List[str], merge_list]
    
    # RAG Context
    retrieved_knowledge: Annotated[List[Dict[str, Any]], operator.add]
    
    # Structured Outputs (Accumulated over the graph execution)
    findings: Annotated[List[str], merge_list]
    evidence_citations: Annotated[List[str], merge_list]
    risk_score: Optional[float]
    risk_level: Optional[str]
    recommendations: Annotated[List[str], merge_list]
    
    # Raw Node Responses (for debugging/traceability)
    node_responses: Annotated[Dict[str, Any], merge_dict]
    
    # Error Handling
    errors: Annotated[List[str], merge_list]
    
    # Iteration limit
    iteration_count: int
