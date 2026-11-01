import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "HR Leave Tools",
    host="127.0.0.1",
    port=8001,
    json_response=True,
)

API_URL = "http://127.0.0.1:8000"


@mcp.tool()
async def apply_leave(
    employee_code: str,
    leave_type: str,
) -> dict:
    """Submit a leave request for a validated demo employee.

    Leave types: annual, sick, casual.
    Submission is not approval.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{API_URL}/leave/apply",
            json={
                "employee_code": employee_code,
                "leave_type": leave_type,
            },
        )

    if response.is_error:
        return {
            "success": False,
            "error": response.text,
        }

    return {
        "success": True,
        "leave_request": response.json(),
    }


@mcp.tool()
async def get_leave_requests() -> dict:
    """Retrieve submitted leave requests from the HR API."""
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{API_URL}/leave/requests"
        )

    response.raise_for_status()

    return {
        "requests": response.json(),
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")