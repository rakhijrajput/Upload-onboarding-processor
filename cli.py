"""Optional command-line entry point for the same processing core."""
import argparse
from pathlib import Path

from onboarding.generator import generate_batch
from onboarding.logging_config import configure_logging
from onboarding.readers import read_employee_rows
from onboarding.templates import validate_template
from onboarding.validation import validate_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate employee onboarding text files.")
    parser.add_argument("roster", help="Path to .csv or .xlsx roster")
    parser.add_argument("template", help="Path to UTF-8 text template")
    parser.add_argument("--output", default="output", help="Output directory (default: output)")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    configure_logging(base / "logs")
    template = Path(args.template).read_text(encoding="utf-8-sig")
    validate_template(template, {"employee_id", "name", "department", "role", "joining_date", "manager"})
    rows = read_employee_rows(args.roster, Path(args.roster).read_bytes())
    valid, issues = validate_rows(rows)
    run_dir, summary = generate_batch(valid, issues, template, Path(args.output))
    print(f"Output: {run_dir}")
    print(f"Summary: {summary['totals']}")


if __name__ == "__main__":
    main()
