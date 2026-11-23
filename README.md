# DealerOS Reconciliation

A small Django application that imports two CSV ledgers, compares their records, and displays disagreements. It includes a server-rendered table and a JSON API.

## Features

- Imports 120 System A records and 121 System B entries into SQLite. The import command can be run repeatedly without duplicating records.
- Compares System B values with System A `total_value`, using `Decimal` for exact monetary comparisons.
- Normalizes record references and keeps raw references and values. Blank or invalid amounts remain unknown rather than being treated as zero.
- Reports missing entries, orphan entries, duplicates, value mismatches, date mismatches, location mismatches, and voided records that still have a System B entry.
- Treats multiple System B entries that sum exactly to the System A total as a split, not a duplicate.
- Filters results by organization on the server. For a cross-organization location mismatch, the row is shown with the System A organization and the other organization's location is hidden.

## Requirements

- Python 3.11 or newer
- pip

## Run locally

From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, you can invoke the environment's Python directly as `.venv\Scripts\python.exe`.

Apply migrations, import the CSV data, and start the development server:

```powershell
python manage.py migrate
python manage.py import_data
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to use the table. The importer prints the number of CSV rows read and saved. Expected counts are `A: 120` and `B: 121`.

## API

The organization parameter is required:

```text
GET /api/disagreements/?org=ORG-A
```

Optional query parameters:

- `reason`: filter by a reason such as `VALUE_MISMATCH` or `MISSING_IN_B`
- `sort`: `value` or `-value` to sort by value ascending or descending

Example:

```text
/api/disagreements/?org=ORG-A&reason=VALUE_MISMATCH&sort=-value
```

The response is a JSON array with each disagreement's reason, record ID, locations, values, and difference. The UI provides an organization selector, a reason filter, and value sorting.

## Tests

Run the test suite from the repository root:

```powershell
python -m pytest
```

Tests cover comparison rules, cleaning edge cases, tenant filtering, and value sorting.

## Decisions and limitations

- Compare System B's amount with System A's `total_value`, not `base_value`.
- A voided System A record with a System B entry is reported as `VOIDED_WITH_B_ENTRY`.
- Date and location differences are reported separately.
- For a cross-organization mismatch, the disagreement is attributed to the organization that owns the System A record; the other organization's location is redacted.
- This is a demonstration app: it has no authentication or authorization. The organization query parameter is a filter, not an identity check. Do not expose it as a production multi-tenant service without adding authenticated, server-enforced access controls.
- The UI uses a Django template instead of React to keep the application small and easy to run.

## Working with an AI assistant

I used an AI assistant in VS Code to inspect the comparison and parsing behavior, make targeted fixes, and run tests. During a new descending-sort regression test, the first assertion mishandled the case where there were no rows with both values missing. Pytest exposed the faulty assertion, which was corrected to check the ordering of populated values.

The part I would review most carefully with a business owner is the cross-organization mismatch policy: whether to attribute the row to System A's organization and redact System B's location. With another day, I would first add authentication and authorization so organization access is based on the signed-in user rather than a query parameter.
