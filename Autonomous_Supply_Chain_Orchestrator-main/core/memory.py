import os
import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from core.config import CHROMA_DB_PATH, OLLAMA_BASE_URL

class MemoryModule:
    def __init__(self, collection_name="supply_chain_memory"):
        print(f"[MemoryModule] Initializing ChromaDB at '{CHROMA_DB_PATH}' with collection '{collection_name}'...")
        
        try:
            # Initialize Embeddings
            self.embeddings = OllamaEmbeddings(
                base_url=OLLAMA_BASE_URL,
                model="nomic-embed-text",  # Defaulting to a common embedding model
            )
            
            # Initialize Chroma
            self.vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=CHROMA_DB_PATH
            )
            print("[MemoryModule] Memory ready.")
            
        except Exception as e:
            print(f"[MemoryModule] Initialization failed: {e}")
            self.vector_store = None

    def store_memory(self, text: str, metadata: dict = None):
        """Stores a text snippet with optional metadata."""
        if not self.vector_store:
            print("[MemoryModule] Error: Vector store not initialized.")
            return

        try:
            self.vector_store.add_texts(texts=[text], metadatas=[metadata] if metadata else None)
            print(f"[MemoryModule] Stored memory: {text[:50]}...")
        except Exception as e:
            print(f"[MemoryModule] Error storing memory: {e}")
    
    def retrieve_context(self, query: str, top_k=3):
        """Retrieves relevant context for a query."""
        if not self.vector_store:
            return ["Error: Vector store not initialized."]

        try:
            # Check if collection is empty
            if self.vector_store._collection.count() == 0:
                 return []

            docs = self.vector_store.similarity_search(query, k=top_k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"[MemoryModule] Error retrieving context: {e}")
            return [f"Error retrieving context: {e}"]
