"""Create employee-specific folders and onboarding text files."""
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from .models import Employee
from .reporting import write_reports
from .templates import render_template

logger = logging.getLogger(__name__)


def safe_folder_name(employee_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", employee_id).strip("._-")
    if not cleaned:
        raise ValueError("Employee ID cannot be converted to a safe folder name.")
    return cleaned[:80]


def generate_batch(valid_rows: list[tuple[int, Employee]], issues: list[dict], template: str, output_root: Path, *, overwrite: bool = False) -> tuple[Path, dict]:
    """Generate files and reports. Invalid rows are included in the CSV report."""
    run_started = datetime.now(timezone.utc)
    run_id = run_started.strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / f"run_{run_id}"
    suffix = 1
    while run_dir.exists():
        run_dir = output_root / f"run_{run_id}_{suffix}"
        suffix += 1
    run_dir.mkdir(parents=True, exist_ok=False)
    results = [dict(row=item["row"], employee_id=item["employee_id"], status=item.get("status", "invalid"), output_file="", errors=item["errors"]) for item in issues]

    for row_number, employee in valid_rows:
        folder = run_dir / safe_folder_name(employee.employee_id)
        file_path = folder / "onboarding.txt"
        try:
            if file_path.exists() and not overwrite:
                results.append({"row": row_number, "employee_id": employee.employee_id, "status": "skipped", "output_file": str(file_path.relative_to(run_dir)), "errors": "Output already exists"})
                continue
            folder.mkdir(parents=True, exist_ok=True)
            text = render_template(template, employee.template_values())
            file_path.write_text(text, encoding="utf-8")
            results.append({"row": row_number, "employee_id": employee.employee_id, "status": "processed", "output_file": str(file_path.relative_to(run_dir)), "errors": ""})
        except Exception as exc:
            logger.exception("Failed processing row %s in run %s", row_number, run_id)
            results.append({"row": row_number, "employee_id": employee.employee_id, "status": "invalid", "output_file": "", "errors": str(exc)})

    summary = write_reports(run_dir, run_id, run_started, results)
    logger.info("Completed run %s: processed=%s invalid=%s skipped=%s", run_id, summary["totals"]["processed"], summary["totals"]["invalid"], summary["totals"]["skipped"])
    return run_dir, summary
