# Employee Onboarding Document Processor

A small Python project that validates a CSV/XLSX employee roster, fills a text template, creates one folder per employee, and writes processing reports. It includes a Streamlit review UI and an optional command-line runner.

## Run the interactive app

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Upload both `sample_data/employees.csv` and `templates/welcome.txt` to try the demo. The app has three pages: add one employee with a form, process a CSV/XLSX roster, and search/filter saved employee history. Valid form submissions are appended to `data/employees.csv`; duplicate IDs are rejected. The roster-processing page shows valid and invalid rows, lets you choose valid employees, previews a generated document, and offers a ZIP download.

## Input format

Required headers (case and whitespace are normalized): `employee_id`, `name`, `department`, `role`, `joining_date`, `manager`.

Accepted joining date formats: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, and `DD-MM-YYYY`. If Excel stores employee IDs as numbers, leading zeros may already be lost; format that column as Text before saving.

Template placeholders use double braces, for example `{{ name }}`, `{{ role }}`, and `{{ joining_date }}`. Supported fields are the six required columns.

## Employee form and history

The **Add employee** page validates required fields and joining date before writing to the master CSV. Employee IDs are checked case-insensitively for duplicates. Invalid or duplicate form submissions are shown on screen and are not saved. The **Employee history** page searches across employee fields, filters by department, and can export the filtered view as CSV.

This demo stores the master CSV locally. Do not use real employee data in a shared or public deployment until access controls, storage location, backup, and retention are defined.

## Output

Each run is stored under `output/run_<UTC timestamp>/`, with an employee-ID folder and `onboarding.txt` per generated employee. The run also includes `processing_summary.csv` and `run_summary.json`. General application logs go to `logs/app.log`; the logger avoids writing employee names or full records.

## Command-line use

```bash
python cli.py sample_data/employees.csv templates/welcome.txt --output output
```

## Tests

```bash
python -m unittest discover -s tests -v
```

This is a learning/demo starter. Before using it with real employee records, add your organization's authentication, access controls, approved storage, retention, and review requirements. Use fictional data for demos.
