import os
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

def get_llm() -> BaseChatModel:
    """
    Returns the configured local LLM provider.
    As per ADR-009, this defaults to Ollama running locally.
    """
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # We allow overriding the model via env variables
    model_name = os.environ.get("LLM_MODEL_NAME", "llama3.1")
    
    # LangChain ChatOllama configuration
    llm = ChatOllama(
        base_url=ollama_base_url,
        model=model_name,
        temperature=0.1, # Low temperature for more deterministic analysis
        # max_tokens limit to prevent infinite generation
        num_predict=2000, 
    )
    
    return llm
