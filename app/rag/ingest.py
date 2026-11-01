from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from app.config import (
    DOCUMENTS_DIR,
    CHROMA_DIR,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
)


def index_policy(folder_name: str, collection_name: str):
    folder = DOCUMENTS_DIR / folder_name
    documents = []

    for path in folder.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        documents.append(
            Document(
                page_content=text,
                metadata={"source": path.name},
            )
        )

    if not documents:
        raise ValueError(f"No TXT documents found in {folder}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

    # Recreate this collection to avoid duplicate chunks
    # when running ingestion again.
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    vectorstore.delete_collection()

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    vectorstore.add_documents(chunks)

    print(f"Indexed {len(chunks)} chunks: {collection_name}")


if __name__ == "__main__":
    index_policy("company_policy", "company_policy")
    index_policy("leave_policy", "leave_policy")