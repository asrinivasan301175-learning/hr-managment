from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from app.config import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
)

def get_retriever(collection_name: str):
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    return vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )
