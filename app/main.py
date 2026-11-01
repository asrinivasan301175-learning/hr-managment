from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
import re
from app.api.leave_api import router as leave_router
from app.agents.supervisor import hr_graph

sessions: dict[str, dict] = {}

class ChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None
    employee_code: str | None = None
    leave_type: str | None = None


app = FastAPI(
    title="HR Multi-Agent API",
    version="1.0.0",
)

app.include_router(leave_router)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat")
async def chat(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid4())
    previous = sessions.get(conversation_id, {})

    query = request.query.strip()

    employee_code = (
        request.employee_code
        or previous.get("employee_code")
    )
    leave_type = (
        request.leave_type
        or previous.get("leave_type")
    )

    # Let users reply naturally with just their employee code.
    code_match = re.search(
        r"\bEMP\d+\b",
        query,
        re.IGNORECASE,
    )
    if code_match:
        employee_code = code_match.group(0).upper()

    # Recognize the demo leave types.
    normalized_query = query.lower()
    for option in ("annual", "sick", "casual"):
        if normalized_query.strip(" .,!") == option:
            leave_type = option
            break

    initial_state = {
        "query": query,
        "employee_code": employee_code,
        "leave_type": leave_type,
        "pending": previous.get("pending", False),
    }

    result = await hr_graph.ainvoke(initial_state)

    sessions[conversation_id] = {
        "pending": result.get("pending", False),
        "employee_code": result.get("employee_code"),
        "leave_type": (
            result.get("leave_type")
            if result.get("pending", False)
            else None
        ),
    }

    return {
        "conversation_id": conversation_id,
        "answer": result.get("answer", "No response generated."),
        "pending": result.get("pending", False),
    }