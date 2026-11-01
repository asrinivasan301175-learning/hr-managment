from threading import Lock

leave_records = []
store_lock = Lock()

valid_employee_codes = {
    "EMP001",
    "EMP002",
    "EMP003",
}

valid_leave_types = {
    "annual",
    "sick",
    "casual",
}