from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = BASE_DIR / "documents"
CHROMA_DIR = BASE_DIR / "chroma_db"

LLM_MODEL = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_BASE_URL = "http://localhost:11434"

COMPANY_COLLECTION = "company_policy"
LEAVE_COLLECTION = "leave_policy"