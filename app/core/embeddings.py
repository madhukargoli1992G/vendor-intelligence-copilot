from langchain_ollama import OllamaEmbeddings
from app.core.config import EMBEDDING_MODEL, OLLAMA_BASE_URL

embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_BASE_URL
)