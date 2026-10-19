"""Write machine-readable processing reports."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def write_reports(output_dir: Path, run_id: str, started_at: datetime, results: list[dict]) -> dict:
    report_path = output_dir / "processing_summary.csv"
    with report_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["row", "employee_id", "status", "output_file", "errors"])
        writer.writeheader()
        writer.writerows(results)

    counts = {
        "processed": sum(item["status"] == "processed" for item in results),
        "invalid": sum(item["status"] == "invalid" for item in results),
        "skipped": sum(item["status"] == "skipped" for item in results),
    }
    summary = {
        "run_id": run_id,
        "started_at_utc": started_at.isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "totals": counts,
        "report_file": report_path.name,
    }
    (output_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
