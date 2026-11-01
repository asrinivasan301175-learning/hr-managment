from pydantic import BaseModel, Field


class LeaveRequest(BaseModel):
    employee_code: str = Field(
        min_length=6,
        max_length=20,
    )
    leave_type: str = Field(
        min_length=2,
        max_length=30,
    )


class LeaveResponse(BaseModel):
    request_id: str
    employee_code: str
    leave_type: str
    status: str