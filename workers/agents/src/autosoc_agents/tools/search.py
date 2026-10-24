from langchain_core.tools import tool
from autosoc_agents.rag.retriever import retriever

@tool
def search_threat_intel(query: str) -> str:
    """
    Search the local threat intelligence knowledge base for information 
    about specific IPs, domains, hashes, or MITRE ATT&CK techniques.
    Do not use this tool for internal network logs.
    """
    results = retriever.search_knowledge(query)
    if not results:
        return "No threat intel found for query."
    
    formatted = []
    for idx, r in enumerate(results):
        formatted.append(f"[{idx+1}] Title: {r['title']}\nContent: {r['content']}\nSource: {r['url']}")
    
    return "\n\n".join(formatted)

@tool
def get_incident_details(incident_id: str) -> str:
    """
    Retrieve the full details of an incident including all alerts and events.
    Use this to get the base context before investigating.
    """
    return f"Incident {incident_id} details (mocked). Status: Open. Severity: High."
