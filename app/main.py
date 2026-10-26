import csv
import io
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.validator import validate_records

app = FastAPI(
    title="DataGuard — CSV Data Quality API",
    description="Validate CSV data, identify quality issues, and retrieve saved reports.",
    version="1.0.0",
)

REPORT_DIR = Path("reports")
MAX_FILE_BYTES = 2_000_000
REQUIRED_COLUMNS = {"name", "email", "amount"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "dataguard-api"}

@app.post("/validate")
async def validate_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded CSV is empty.")
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. Maximum size is 2 MB.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must use UTF-8 encoding.")

    try:
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV must include a header row.")

        normalized_headers = {h.strip().lower() for h in reader.fieldnames if h}
        missing = sorted(REQUIRED_COLUMNS - normalized_headers)
        if missing:
            raise HTTPException(
                status_code=400,
                detail={"message": "Required columns are missing.", "missing_columns": missing},
            )

        records = list(reader)
    except csv.Error:
        raise HTTPException(status_code=400, detail="Could not parse the CSV file.")

    if not records:
        raise HTTPException(status_code=400, detail="CSV contains a header but no data rows.")

    results, summary = validate_records(records)
    report_id = str(uuid.uuid4())
    report = {
        "report_id": report_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "filename": Path(file.filename).name,
        "summary": summary,
        "rows": results,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{report_id}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return JSONResponse(content=report)

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    # Accept UUID-shaped IDs only; prevents arbitrary path input.
    try:
        safe_id = str(uuid.UUID(report_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid report ID.")

    report_path = REPORT_DIR / f"{safe_id}.json"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found.")

    return json.loads(report_path.read_text(encoding="utf-8"))
