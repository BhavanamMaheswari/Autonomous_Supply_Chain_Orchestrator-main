from langchain_ollama import ChatOllama
from core.config import OLLAMA_BASE_URL, MODEL_REASONING, MODEL_FAST, MODEL_TOOL

def get_llm(role: str):
    """
    Differential Routing: Returns the appropriate model based on the agent's role.
    
    Roles:
    - "reasoning": High-token reasoning (DeepSeek-R1)
    - "fast": Low-latency monitoring (Llama 3.2)
    - "tool": Reliable tool usage (Mistral)
    """
    if role == "reasoning":
        return ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=MODEL_REASONING,
            temperature=0.7 # Higher temperature for creative reasoning? Or low for strict logic? R1 usually handles its own thinking.
        )
    elif role == "fast":
        return ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=MODEL_FAST,
            temperature=0.1
        )
    elif role == "tool":
        return ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=MODEL_TOOL,
            temperature=0.1
        )
    else:
        raise ValueError(f"Unknown role: {role}")

# Global instances (lazy loading preferred in app, but here for convenience)
llm_reasoning = get_llm("reasoning")
llm_fast = get_llm("fast")
llm_tool = get_llm("tool")
