from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from app.config import LLM_MODEL, OLLAMA_BASE_URL
from app.rag.retrievers import get_retriever


retriever = get_retriever("leave_policy")

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are the Leave Policy Agent.
Answer only from the leave policy context.
Distinguish a policy rule from an employee-specific
leave balance. Never invent a leave balance or
claim that a request has been approved.

Context:
{context}"""
    ),
    ("human", "{question}"),
])


def answer_leave_policy(question: str) -> str:
    docs = retriever.invoke(question)
    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    if not context.strip():
        return "I could not find relevant leave policy information."

    response = (prompt | llm).invoke({
        "context": context,
        "question": question,
    })

    sources = sorted({
        doc.metadata.get("source", "unknown")
        for doc in docs
    })

    return (
        f"{response.content}\n\n"
        f"Sources: {', '.join(sources)}"
    )