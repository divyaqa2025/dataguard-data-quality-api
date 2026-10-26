import re
from collections import Counter
from decimal import Decimal, InvalidOperation

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_records(records):
    """
    Clean simple text fields and validate customer/order-style CSV records.
    Expected columns: name, email, amount.
    Returns a list of row results and aggregate counts.
    """
    cleaned = []
    for index, record in enumerate(records, start=2):  # CSV header is line 1
        row = {str(k).strip().lower(): (v.strip() if isinstance(v, str) else v)
               for k, v in record.items()}
        cleaned.append({
            "source_row": index,
            "name": row.get("name", ""),
            "email": row.get("email", "").lower(),
            "amount": row.get("amount", ""),
            "issues": [],
        })

    email_counts = Counter(r["email"] for r in cleaned if r["email"])

    for row in cleaned:
        if not row["name"]:
            row["issues"].append("missing_name")

        email = row["email"]
        if not email:
            row["issues"].append("missing_email")
        elif not EMAIL_PATTERN.match(email):
            row["issues"].append("invalid_email")

        amount = row["amount"]
        if amount == "":
            row["issues"].append("missing_amount")
        else:
            try:
                parsed_amount = Decimal(amount)
                if not parsed_amount.is_finite() or parsed_amount < 0:
                    row["issues"].append("invalid_amount")
                else:
                    row["amount"] = str(parsed_amount.quantize(Decimal("0.01")))
            except (InvalidOperation, ValueError):
                row["issues"].append("invalid_amount")

        if email and email_counts[email] > 1:
            row["issues"].append("duplicate_email")

        row["is_valid"] = len(row["issues"]) == 0

    valid_count = sum(1 for r in cleaned if r["is_valid"])
    invalid_count = len(cleaned) - valid_count
    issue_counts = Counter(issue for row in cleaned for issue in row["issues"])

    summary = {
        "total_rows": len(cleaned),
        "valid_rows": valid_count,
        "invalid_rows": invalid_count,
        "issue_counts": dict(sorted(issue_counts.items())),
    }
    return cleaned, summary
