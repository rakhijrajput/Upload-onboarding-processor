"""CSV storage for manually added, validated employee records."""
import csv
from pathlib import Path
from typing import Any

from .readers import REQUIRED_COLUMNS


class DuplicateEmployeeError(ValueError):
    """Raised when an employee ID is already present in the master CSV."""


def load_master_records(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        headers = [str(name).strip().lower() for name in reader.fieldnames]
        if headers != list(REQUIRED_COLUMNS):
            raise ValueError(
                "The employee history CSV has unexpected columns. "
                f"Expected: {', '.join(REQUIRED_COLUMNS)}."
            )
        records = []
        for raw in reader:
            normalized = {str(key).strip().lower(): value for key, value in raw.items() if key is not None}
            records.append({key: str(normalized.get(key) or "").strip() for key in REQUIRED_COLUMNS})
        return records


def append_employee(csv_path: Path, record: dict[str, Any]) -> None:
    """Append one already-validated record, rejecting duplicate IDs."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    employee_id = str(record.get("employee_id", "")).strip()
    if any(row["employee_id"].casefold() == employee_id.casefold() for row in load_master_records(csv_path)):
        raise DuplicateEmployeeError(f"Employee ID {employee_id} already exists.")

    needs_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS, extrasaction="ignore")
        if needs_header:
            writer.writeheader()
        writer.writerow({key: str(record.get(key, "")).strip() for key in REQUIRED_COLUMNS})
        handle.flush()
