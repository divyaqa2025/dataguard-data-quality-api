# DataGuard — CSV Data Quality API

A small backend project that validates CSV data, reports quality problems, and saves a retrievable JSON report. Built to demonstrate Python fundamentals, API development, input validation, error handling, automated tests, and practical documentation.

## Problem

CSV files often contain missing values, malformed email addresses, duplicate records, and invalid numeric amounts. Manually checking each row is slow and inconsistent.

## What it does

- Accepts a CSV file through a REST API.
- Checks required columns: `name`, `email`, `amount`.
- Trims whitespace and normalizes email addresses to lowercase.
- Flags missing fields, invalid emails, negative/non-numeric amounts, and duplicate emails.
- Returns a row-by-row result plus aggregate issue counts.
- Saves each result as a JSON report and lets a caller retrieve it by report ID.
- Rejects empty files, non-CSV files, missing headers, invalid UTF-8, and files over 2 MB.
- Includes unit and API tests.

## Tech stack

Python, FastAPI, REST, CSV/JSON, pytest, Git.

## Run locally

Use Python 3.10+.

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install and start:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Try it

Upload the included sample CSV using `/validate` in the docs page, or run:

```bash
curl -X POST "http://127.0.0.1:8000/validate" \
  -F "file=@sample_data/customers.csv"
```

The response includes a `report_id`. Retrieve the saved report:

```bash
curl "http://127.0.0.1:8000/reports/PASTE_REPORT_ID_HERE"
```

Health check:

```bash
curl "http://127.0.0.1:8000/health"
```

## Run tests

```bash
pytest -q
```

The tests cover valid records, malformed data, duplicate emails, missing values, API behavior, report retrieval, and invalid uploads.

## API summary

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/validate` | Upload and validate a CSV |
| GET | `/reports/{report_id}` | Retrieve a saved report |

## Example validation rules

| Field / rule | Expected behavior |
|---|---|
| `name` | Must not be blank |
| `email` | Must be present and match a basic email pattern |
| duplicate email | Both matching rows are flagged |
| `amount` | Must be numeric and non-negative |
| valid amount | Normalized to two decimal places |

## Design decisions and limitations

- The validator is separated from the API layer so it can be tested independently.
- Errors use appropriate HTTP status codes and clear messages.
- Reports are stored as local JSON files for this prototype. A production version should use a database, authentication, retention policies, structured logging, and controlled storage.
- Email validation is deliberately basic; it does not prove that an email address exists.
- The project currently processes CSV files synchronously and is intended as a portfolio prototype, not a production service.

## Next improvements

1. Add pagination for large reports.
2. Add configurable schemas and rules.
3. Export invalid rows as a downloadable CSV.
4. Add SQLite/PostgreSQL storage and report expiration.
5. Add CI using GitHub Actions.
6. Add structured logging and performance tests.

## Portfolio description

**DataGuard — CSV Data Quality API:** Built a FastAPI service that validates uploaded CSV datasets, normalizes fields, detects missing values, malformed emails, duplicate emails, and invalid amounts, then produces and stores structured JSON reports. Added input-size/type checks and pytest coverage for validation and API behavior.

Only list features as completed after you have run the application and tests yourself and understand how the code works.
