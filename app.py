from csv import DictWriter
from io import BytesIO, StringIO
from pathlib import Path
import zipfile

import streamlit as st

from onboarding.generator import generate_batch
from onboarding.logging_config import configure_logging
from onboarding.readers import REQUIRED_COLUMNS, read_employee_rows
from onboarding.storage import DuplicateEmployeeError, append_employee, load_master_records
from onboarding.templates import render_template, validate_template
from onboarding.validation import validate_rows

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EMPLOYEE_CSV = DATA_DIR / "employees.csv"
configure_logging(BASE_DIR / "logs")

st.set_page_config(page_title="Onboarding Document Processor", page_icon="🧩", layout="wide")
st.title("Employee Onboarding Document Processor")
st.caption("Add employees, review history, or generate onboarding documents.")

page = st.sidebar.radio(
    "Navigation",
    ["Add employee", "Create documents", "Employee history"],
)


def render_add_employee() -> None:
    st.header("Add an employee")
    st.write("Enter the employee details. Only records that pass validation are saved to the master CSV.")
    with st.form("add_employee_form", clear_on_submit=False):
        left, right = st.columns(2)
        with left:
            employee_id = st.text_input("Employee ID", placeholder="EMP-103")
            name = st.text_input("Full name")
            department = st.text_input("Department")
        with right:
            role = st.text_input("Role")
            joining_date = st.date_input("Joining date")
            manager = st.text_input("Manager")
        submitted = st.form_submit_button("Validate and save employee", type="primary")

    if not submitted:
        return

    candidate = {
        "employee_id": employee_id,
        "name": name,
        "department": department,
        "role": role,
        "joining_date": joining_date,
        "manager": manager,
    }
    valid, issues = validate_rows([candidate])
    if issues:
        st.error("This employee was not saved. Fix the following field(s):")
        for issue in issues:
            st.write(f"- {issue['errors']}")
        return

    employee = valid[0][1]
    record = {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "department": employee.department,
        "role": employee.role,
        "joining_date": employee.joining_date.isoformat(),
        "manager": employee.manager,
    }
    try:
        append_employee(EMPLOYEE_CSV, record)
    except DuplicateEmployeeError as exc:
        st.error(str(exc))
        return
    except (OSError, ValueError) as exc:
        st.error(f"Could not save the employee record: {exc}")
        return
    st.success(f"{employee.name} was validated and saved to employee history.")


def render_process_roster() -> None:
    st.header("Create documents")
    with st.sidebar:
        st.subheader("Roster inputs")
        roster_file = st.file_uploader("Employee roster (.csv or .xlsx)", type=["csv", "xlsx"], key="roster_upload")
        template_file = st.file_uploader("Text template (.txt)", type=["txt"], key="template_upload")
        st.caption("Required columns: employee_id, name, department, role, joining_date, manager.")
        st.caption("In Excel, format employee_id as Text to preserve leading zeros.")

    if not roster_file or not template_file:
        st.info("Upload both files in the sidebar. You can try the files in sample_data/ and templates/.")
        return

    try:
        rows = read_employee_rows(roster_file.name, roster_file.getvalue())
        valid_rows, issues = validate_rows(rows)
        template = template_file.getvalue().decode("utf-8-sig")
        validate_template(template, set(REQUIRED_COLUMNS))
    except (ValueError, UnicodeDecodeError) as exc:
        st.error(str(exc))
        return

    st.subheader("Review records")
    preview_rows = []
    for row_no, employee in valid_rows:
        preview_rows.append({"row": row_no, "employee_id": employee.employee_id, "name": employee.name,
                             "department": employee.department, "role": employee.role,
                             "joining_date": employee.joining_date.isoformat(), "manager": employee.manager,
                             "status": "Valid", "errors": ""})
    for issue in issues:
        preview_rows.append({"row": issue["row"], "employee_id": issue["employee_id"], "name": "",
                             "department": "", "role": "", "joining_date": "", "manager": "",
                             "status": "Needs correction", "errors": issue["errors"]})
    preview_rows.sort(key=lambda item: item["row"])
    st.dataframe(preview_rows, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Valid", len(valid_rows))
    col2.metric("Needs correction", len(issues))
    col3.metric("Total rows", len(rows))

    if not valid_rows:
        st.warning("There are no valid employee rows to process yet.")
        return

    valid_ids = [employee.employee_id for _, employee in valid_rows]
    selected_ids = st.multiselect("Choose employees to generate", valid_ids, default=valid_ids)
    selected = set(selected_ids)
    selected_rows = [(row_no, employee) for row_no, employee in valid_rows if employee.employee_id in selected]
    if selected_rows:
        preview_employee = selected_rows[0][1]
        st.subheader("Preview document")
        st.code(render_template(template, preview_employee.template_values()), language="text")

    if st.button("Generate onboarding files", type="primary", disabled=not selected_rows):
        skipped = [
            {"row": row_no, "employee_id": employee.employee_id, "status": "skipped", "errors": "Not selected for this run"}
            for row_no, employee in valid_rows if employee.employee_id not in selected
        ]
        run_dir, summary = generate_batch(selected_rows, issues + skipped, template, BASE_DIR / "output")
        archive = BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in run_dir.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(run_dir))
        st.success(f"Done. {summary['totals']['processed']} document(s) generated.")
        st.json(summary["totals"])
        st.download_button("Download generated files and reports", data=archive.getvalue(),
                           file_name=f"onboarding_{summary['run_id']}.zip", mime="application/zip")


def render_employee_history() -> None:
    st.header("Employee history")
    try:
        records = load_master_records(EMPLOYEE_CSV)
    except (OSError, ValueError) as exc:
        st.error(f"Could not read employee history: {exc}")
        return

    if not records:
        st.info("No employee records have been saved yet. Add a valid employee from the Add employee page.")
        return

    st.metric("Saved employees", len(records))
    search = st.text_input("Search by employee ID, name, department, role, or manager")
    departments = ["All"] + sorted({row["department"] for row in records if row["department"]})
    chosen_department = st.selectbox("Filter by department", departments)
    filtered = records
    if chosen_department != "All":
        filtered = [row for row in filtered if row["department"] == chosen_department]
    if search.strip():
        query = search.casefold().strip()
        filtered = [row for row in filtered if any(query in row[field].casefold() for field in REQUIRED_COLUMNS)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
    output = StringIO()
    writer = DictWriter(output, fieldnames=REQUIRED_COLUMNS)
    writer.writeheader()
    writer.writerows(filtered)
    st.download_button("Download displayed history as CSV", data=output.getvalue(),
                       file_name="employee_history.csv", mime="text/csv")


if page == "Add employee":
    render_add_employee()
elif page == "Create documents":
    render_process_roster()
else:
    render_employee_history()
