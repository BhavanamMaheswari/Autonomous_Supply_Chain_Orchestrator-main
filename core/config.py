import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# ChromaDB Settings
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# Ollama Models
MODEL_REASONING = os.getenv("OLLAMA_MODEL_REASONING", "deepseek-r1:1.5b")
MODEL_FAST = os.getenv("OLLAMA_MODEL_FAST", "llama3.2")
MODEL_TOOL = os.getenv("OLLAMA_MODEL_TOOL", "llama3.2")

# Ollama Base URL
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Search Settings
SEARCH_PROVIDER = "serper" if SERPER_API_KEY else "duckduckgo"
