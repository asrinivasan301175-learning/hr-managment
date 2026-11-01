import json

from app.mcp_client.client import call_mcp_tool


async def handle_leave_application(
    query: str,
    employee_code: str | None = None,
    leave_type: str | None = None,
) -> dict:
    # Ask for missing fields before invoking any tool.
    if not employee_code:
        return {
            "answer": (
                "I can help you apply for leave. "
                "Please provide your employee code."
            ),
            "pending": True,
        }

    if not leave_type:
        return {
            "answer": (
                "What type of leave would you like to apply for? "
                "Choose annual, sick, or casual."
            ),
            "pending": True,
            "employee_code": employee_code.upper(),
        }

    normalized_type = leave_type.strip().lower()

    if normalized_type not in {"annual", "sick", "casual"}:
        return {
            "answer": (
                "Please choose annual, sick, or casual leave."
            ),
            "pending": True,
            "employee_code": employee_code.upper(),
        }

    result = await call_mcp_tool(
        "apply_leave",
        {
            "employee_code": employee_code.strip().upper(),
            "leave_type": normalized_type,
        },
    )

    # The MCP tool returns JSON content from our server.
    payload = json.loads(result[0])

    if not payload.get("success"):
        return {
            "answer": (
                "I could not submit the leave request. "
                f"Details: {payload.get('error', 'Unknown error')}"
            ),
            "pending": True,
            "employee_code": employee_code.upper(),
            "leave_type": normalized_type,
        }

    leave = payload["leave_request"]

    return {
        "answer": (
            f"Your leave request has been submitted.\n"
            f"Request ID: {leave['request_id']}\n"
            f"Employee: {leave['employee_code']}\n"
            f"Leave type: {leave['leave_type']}\n"
            f"Status: {leave['status']}"
        ),
        "pending": False,
        "employee_code": employee_code.upper(),
        "leave_type": normalized_type,
    }