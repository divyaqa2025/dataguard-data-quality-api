from app.validator import validate_records

def test_valid_row_is_valid_and_amount_is_normalized():
    rows, summary = validate_records([
        {"name": " Asha ", "email": "ASHA@example.com", "amount": "12"}
    ])
    assert rows[0]["is_valid"] is True
    assert rows[0]["name"] == "Asha"
    assert rows[0]["email"] == "asha@example.com"
    assert rows[0]["amount"] == "12.00"
    assert summary["valid_rows"] == 1

def test_invalid_email_and_negative_amount_are_reported():
    rows, summary = validate_records([
        {"name": "Ravi", "email": "not-an-email", "amount": "-3"}
    ])
    assert rows[0]["is_valid"] is False
    assert "invalid_email" in rows[0]["issues"]
    assert "invalid_amount" in rows[0]["issues"]
    assert summary["invalid_rows"] == 1

def test_duplicate_emails_are_flagged_for_both_rows():
    rows, summary = validate_records([
        {"name": "A", "email": "same@example.com", "amount": "1"},
        {"name": "B", "email": "SAME@example.com", "amount": "2"},
    ])
    assert "duplicate_email" in rows[0]["issues"]
    assert "duplicate_email" in rows[1]["issues"]
    assert summary["issue_counts"]["duplicate_email"] == 2

def test_missing_fields_are_reported():
    rows, summary = validate_records([{"name": "", "email": "", "amount": ""}])
    assert set(rows[0]["issues"]) == {"missing_name", "missing_email", "missing_amount"}
    assert summary["invalid_rows"] == 1
