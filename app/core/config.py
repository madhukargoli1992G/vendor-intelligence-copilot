import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")

QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "vendor_docs")