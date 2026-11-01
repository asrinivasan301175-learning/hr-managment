from typing import Optional, TypedDict
from langgraph.graph import StateGraph, START, END

from app.agents.company_policy_agent import answer_company_policy
from app.agents.leave_policy_agent import answer_leave_policy
from app.agents.leave_application_agent import (
    handle_leave_application,
)


class HRState(TypedDict, total=False):
    query: str
    employee_code: Optional[str]
    leave_type: Optional[str]
    pending: bool
    intent: str
    answer: str


def classify_intent(state: HRState) -> dict:
    query = state.get("query", "").lower()

    # Continue an incomplete leave application first.
    if state.get("pending", False):
        return {"intent": "leave_application"}

    application_phrases = (
        "apply for leave",
        "apply leave",
        "request leave",
        "submit leave",
        "take leave",
    )

    if any(phrase in query for phrase in application_phrases):
        return {"intent": "leave_application"}

    leave_policy_terms = (
        "leave policy",
        "annual leave",
        "sick leave policy",
        "leave entitlement",
        "leave eligibility",
        "leave balance",
        "leave rules",
    )

    if any(term in query for term in leave_policy_terms):
        return {"intent": "leave_policy"}

    return {"intent": "company_policy"}


def route_to_agent(state: HRState) -> str:
    return state["intent"]


def company_policy_node(state: HRState) -> dict:
    answer = answer_company_policy(state["query"])
    return {"answer": answer, "pending": False}


def leave_policy_node(state: HRState) -> dict:
    answer = answer_leave_policy(state["query"])
    return {"answer": answer, "pending": False}


async def leave_application_node(state: HRState) -> dict:
    result = await handle_leave_application(
        query=state["query"],
        employee_code=state.get("employee_code"),
        leave_type=state.get("leave_type"),
    )

    return result


builder = StateGraph(HRState)

builder.add_node("supervisor", classify_intent)
builder.add_node("company_policy", company_policy_node)
builder.add_node("leave_policy", leave_policy_node)
builder.add_node("leave_application", leave_application_node)

builder.add_edge(START, "supervisor")

builder.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {
        "company_policy": "company_policy",
        "leave_policy": "leave_policy",
        "leave_application": "leave_application",
    },
)

builder.add_edge("company_policy", END)
builder.add_edge("leave_policy", END)
builder.add_edge("leave_application", END)

hr_graph = builder.compile()