from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Employee:
    employee_id: str
    name: str
    department: str
    role: str
    joining_date: date
    manager: str

    def template_values(self) -> dict[str, str]:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "department": self.department,
            "role": self.role,
            "joining_date": f"{self.joining_date.strftime('%B')} {self.joining_date.day}, {self.joining_date.year}",
            "manager": self.manager,
        }
