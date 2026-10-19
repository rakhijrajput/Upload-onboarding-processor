"""Employee row validation with row-specific error messages."""
from datetime import date, datetime
from typing import Any

from .models import Employee
from .readers import REQUIRED_COLUMNS


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _clean(value)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("Use YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, or DD-MM-YYYY.")


def validate_rows(rows: list[dict[str, Any]]) -> tuple[list[tuple[int, Employee]], list[dict[str, Any]]]:
    """Return valid (CSV/XLSX row number, Employee) pairs and issue records."""
    valid: list[tuple[int, Employee]] = []
    issues: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row_number, raw in enumerate(rows, start=2):  # header is row 1
        row = {str(key).strip().lower(): value for key, value in raw.items()}
        errors = []
        missing_columns = [field for field in REQUIRED_COLUMNS if field not in row]
        if missing_columns:
            issues.append({"row": row_number, "employee_id": "", "status": "invalid", "errors": f"Missing columns: {', '.join(missing_columns)}"})
            continue

        employee_id = _clean(row.get("employee_id"))
        values = {field: _clean(row.get(field)) for field in REQUIRED_COLUMNS}
        for field in REQUIRED_COLUMNS:
            if not values[field]:
                errors.append(f"{field.replace('_', ' ').title()} is required")
        if employee_id and employee_id in seen_ids:
            errors.append("Employee ID is duplicated in this upload")
        elif employee_id:
            seen_ids.add(employee_id)

        try:
            joining_date = _parse_date(row.get("joining_date"))
        except ValueError as exc:
            joining_date = None
            errors.append(f"Joining date is invalid: {exc}")

        if errors:
            issues.append({"row": row_number, "employee_id": employee_id, "status": "invalid", "errors": "; ".join(errors)})
            continue

        valid.append((row_number, Employee(
            employee_id=employee_id,
            name=values["name"],
            department=values["department"],
            role=values["role"],
            joining_date=joining_date,
            manager=values["manager"],
        )))
    return valid, issues
