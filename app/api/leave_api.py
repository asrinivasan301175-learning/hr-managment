from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.database.store import (
    leave_records,
    store_lock,
    valid_employee_codes,
    valid_leave_types,
)
from app.schemas.leave import LeaveRequest, LeaveResponse


router = APIRouter(prefix="/leave", tags=["Leave"])


@router.post("/apply", response_model=LeaveResponse)
def apply_leave(request: LeaveRequest):
    employee_code = request.employee_code.strip().upper()
    leave_type = request.leave_type.strip().lower()

    if employee_code not in valid_employee_codes:
        raise HTTPException(
            status_code=400,
            detail="Invalid employee code",
        )

    if leave_type not in valid_leave_types:
        raise HTTPException(
            status_code=400,
            detail="Leave type must be annual, sick, or casual",
        )

    record = {
        "request_id": str(uuid4()),
        "employee_code": employee_code,
        "leave_type": leave_type,
        "status": "Submitted - Pending Approval",
    }

    with store_lock:
        leave_records.append(record)

    return record


@router.get("/requests")
def get_leave_requests():
    with store_lock:
        return list(leave_records) 