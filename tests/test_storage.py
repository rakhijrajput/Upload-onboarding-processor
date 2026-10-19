import csv
import tempfile
import unittest
from pathlib import Path

from onboarding.storage import DuplicateEmployeeError, append_employee, load_master_records


class StorageTests(unittest.TestCase):
    def test_append_and_load(self):
        record = {"employee_id": "EMP-001", "name": "Sam Lee", "department": "IT", "role": "Engineer", "joining_date": "2026-11-02", "manager": "Rae"}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "data" / "employees.csv"
            append_employee(path, record)
            self.assertEqual(load_master_records(path), [record])

    def test_duplicate_id_is_rejected_case_insensitively(self):
        record = {"employee_id": "EMP-001", "name": "Sam Lee", "department": "IT", "role": "Engineer", "joining_date": "2026-11-02", "manager": "Rae"}
        duplicate = dict(record, employee_id="emp-001")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "employees.csv"
            append_employee(path, record)
            with self.assertRaises(DuplicateEmployeeError):
                append_employee(path, duplicate)


if __name__ == "__main__":
    unittest.main()
