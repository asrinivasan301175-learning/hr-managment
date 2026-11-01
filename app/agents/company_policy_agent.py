from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from app.config import LLM_MODEL, OLLAMA_BASE_URL
from app.rag.retrievers import get_retriever

retriever = get_retriever("company_policy")

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are the Company Policy Agent.
Answer only using the supplied company policy context.
If the answer is not in the context, say that the
company handbook does not contain enough information.
Do not invent company rules.

Context:
{context}"""
    ),
    ("human", "{question}"),
])


def answer_company_policy(question: str) -> str:
    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    if not context.strip():
        return "I could not find relevant company policy information."

    chain = prompt | llm
    response = chain.invoke({
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