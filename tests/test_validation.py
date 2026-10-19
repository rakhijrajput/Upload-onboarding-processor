import unittest
from datetime import date

from onboarding.validation import validate_rows


class ValidationTests(unittest.TestCase):
    def test_valid_row_and_date_formats(self):
        rows = [{"employee_id": "0012", "name": "Sam Lee", "department": "IT", "role": "Engineer", "joining_date": "2026-11-02", "manager": "Rae"}]
        valid, issues = validate_rows(rows)
        self.assertEqual(issues, [])
        self.assertEqual(valid[0][1].employee_id, "0012")
        self.assertEqual(valid[0][1].joining_date, date(2026, 11, 2))

    def test_missing_field_and_duplicate_id(self):
        base = {"employee_id": "A1", "name": "A", "department": "IT", "role": "Dev", "joining_date": "2026-11-02", "manager": "M"}
        second = dict(base, name="")
        valid, issues = validate_rows([base, second])
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(issues), 1)
        self.assertIn("Name is required", issues[0]["errors"])
        self.assertIn("duplicated", issues[0]["errors"])

    def test_unknown_date_fails(self):
        row = {"employee_id": "A1", "name": "A", "department": "IT", "role": "Dev", "joining_date": "not-a-date", "manager": "M"}
        valid, issues = validate_rows([row])
        self.assertEqual(valid, [])
        self.assertIn("Joining date is invalid", issues[0]["errors"])


if __name__ == "__main__":
    unittest.main()
