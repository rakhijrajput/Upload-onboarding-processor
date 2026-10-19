import tempfile
import unittest
from datetime import date
from pathlib import Path

from onboarding.generator import generate_batch
from onboarding.models import Employee


class GeneratorTests(unittest.TestCase):
    def test_reports_skipped_records(self):
        employee = Employee("E-1", "Sam Lee", "IT", "Engineer", date(2026, 11, 2), "Rae")
        with tempfile.TemporaryDirectory() as temporary:
            run_dir, summary = generate_batch(
                [(2, employee)],
                [{"row": 3, "employee_id": "E-2", "status": "skipped", "errors": "Not selected"}],
                "Welcome {{ name }}",
                Path(temporary),
            )
            self.assertTrue((run_dir / "E-1" / "onboarding.txt").is_file())
            self.assertEqual(summary["totals"], {"processed": 1, "invalid": 0, "skipped": 1})


if __name__ == "__main__":
    unittest.main()
