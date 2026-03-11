from langchain_ollama import ChatOllama
from app.core.config import LLM_MODEL, OLLAMA_BASE_URL

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.2,
)