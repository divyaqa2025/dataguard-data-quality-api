from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_validate_csv_and_fetch_saved_report(tmp_path, monkeypatch):
    monkeypatch.setattr("app.main.REPORT_DIR", tmp_path)
    csv_content = "name,email,amount\nAsha,asha@example.com,12\nRavi,bad-email,-2\n"
    response = client.post(
        "/validate",
        files={"file": ("customers.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_rows"] == 2
    assert data["summary"]["valid_rows"] == 1
    assert data["summary"]["invalid_rows"] == 1

    saved = client.get(f"/reports/{data['report_id']}")
    assert saved.status_code == 200
    assert saved.json()["report_id"] == data["report_id"]

def test_non_csv_file_is_rejected():
    response = client.post(
        "/validate",
        files={"file": ("notes.txt", "hello", "text/plain")},
    )
    assert response.status_code == 400

def test_missing_columns_are_rejected():
    response = client.post(
        "/validate",
        files={"file": ("bad.csv", "name,email\nAsha,asha@example.com\n", "text/csv")},
    )
    assert response.status_code == 400
