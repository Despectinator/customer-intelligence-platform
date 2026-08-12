"""
CSV parsing, per-row validation, customer matching/creation, and a single
batch recompute at the end of an upload. See
docs/architecture/CSV-Upload-Flow.md for the full design.
"""
import csv
import io
import uuid
from datetime import date
from decimal import Decimal, InvalidOperation

from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import Customer, Transaction
from app.schemas.upload import UploadResult, UploadRowError
from app.services import analytics_service

REQUIRED_COLUMNS = {"first_name", "last_name", "email", "order_date", "order_amount"}


def _parse_row(row: dict, row_number: int) -> tuple[dict, str] | tuple[None, str]:
    """
    Validates and normalizes a single CSV row. Returns (parsed_dict, None)
    on success, or (None, error_reason) on failure — never raises, since
    validation failures here are expected, routine outcomes, not bugs.
    """
    first_name = (row.get("first_name") or "").strip()
    last_name = (row.get("last_name") or "").strip()
    email = (row.get("email") or "").strip()

    if not first_name or not last_name or not email:
        return None, "first_name, last_name, and email are all required"

    try:
        # check_deliverability=False: this only validates the email's
        # *format*, matching what Pydantic's EmailStr does on the regular
        # POST /customers endpoint — it does not attempt to verify the
        # domain actually receives mail, which would require a network
        # call and isn't appropriate for bulk row validation.
        validated = validate_email(email, check_deliverability=False)
        email = validated.normalized
    except EmailNotValidError as e:
        return None, f"email '{email}' is not valid: {e}"

    order_date_raw = (row.get("order_date") or "").strip()
    try:
        order_date = date.fromisoformat(order_date_raw)
    except ValueError:
        return None, f"order_date '{order_date_raw}' could not be parsed (expected YYYY-MM-DD)"

    order_amount_raw = (row.get("order_amount") or "").strip()
    try:
        order_amount = Decimal(order_amount_raw)
    except InvalidOperation:
        return None, f"order_amount '{order_amount_raw}' is not a number"
    if order_amount <= 0:
        return None, "order_amount must be a positive number"

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": (row.get("phone") or "").strip() or None,
        "company": (row.get("company") or "").strip() or None,
        "order_date": order_date,
        "order_amount": order_amount,
        "payment_method": (row.get("payment_method") or "").strip() or None,
    }, None


def _transaction_key(
    customer_id: uuid.UUID,
    order_date: date,
    order_amount: Decimal,
    payment_method: str | None,
) -> tuple:
    normalized_payment_method = (
        payment_method.strip().lower() if payment_method else None
    )
    return customer_id, order_date, order_amount, normalized_payment_method


def process_csv_upload(db: Session, project_id: uuid.UUID, file_contents: str) -> UploadResult:
    reader = csv.DictReader(io.StringIO(file_contents))

    if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        # A missing required column is a structural problem with the file
        # itself, not "some rows succeeded, some didn't" — the endpoint
        # can't process this file at all, so it's a real 400, not a 200
        # with an errors array pretending partial success was attempted.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required column(s): {', '.join(sorted(missing))}",
        )

    # Cache of email -> customer_id, seeded with existing customers in this
    # project so repeated emails within the same file (or already in the
    # DB) attach to the same customer instead of creating duplicates.
    existing_customers = {
        c.email: c.id
        for c in db.query(Customer).filter(Customer.project_id == project_id).all()
        if c.email
    }

    existing_transaction_keys = {
        _transaction_key(
            transaction.customer_id,
            transaction.order_date,
            transaction.order_amount,
            transaction.payment_method,
        )
        for transaction in (
            db.query(Transaction)
            .join(Customer, Transaction.customer_id == Customer.id)
            .filter(Customer.project_id == project_id)
            .all()
        )
    }
    upload_transaction_keys = set()

    customers_created = 0
    transactions_inserted = 0
    rows_skipped = 0
    errors: list[UploadRowError] = []
    affected_customer_ids: set[uuid.UUID] = set()

    for row_number, raw_row in enumerate(reader, start=2):  # row 1 is the header
        parsed, error = _parse_row(raw_row, row_number)
        if error:
            rows_skipped += 1
            errors.append(UploadRowError(row=row_number, reason=error))
            continue

        customer_id = existing_customers.get(parsed["email"])
        if customer_id is None:
            customer = Customer(
                project_id=project_id,
                first_name=parsed["first_name"],
                last_name=parsed["last_name"],
                email=parsed["email"],
                phone=parsed["phone"],
                company=parsed["company"],
            )
            db.add(customer)
            db.flush()  # assigns customer.id without committing yet
            customer_id = customer.id
            existing_customers[parsed["email"]] = customer_id
            customers_created += 1

        existing_transaction = (
            db.query(Transaction)
            .filter(
                Transaction.customer_id == customer_id,
                Transaction.order_date == parsed["order_date"],
                Transaction.order_amount == parsed["order_amount"],
                Transaction.payment_method == parsed["payment_method"],
            )
            .first()
        )

        if existing_transaction:
            rows_skipped += 1
            errors.append(
                UploadRowError(
                    row=row_number,
                    reason="Duplicate transaction already exists",
                )
            )
            continue

        transaction_key = _transaction_key(
            customer_id,
            parsed["order_date"],
            parsed["order_amount"],
            parsed["payment_method"],
        )

        if (
            transaction_key in existing_transaction_keys
            or transaction_key in upload_transaction_keys
        ):
            rows_skipped += 1
            errors.append(
                UploadRowError(
                    row=row_number,
                    reason="Duplicate transaction already exists",
                )
            )
            continue

        db.add(
            Transaction(
                customer_id=customer_id,
                order_date=parsed["order_date"],
                order_amount=parsed["order_amount"],
                payment_method=parsed["payment_method"],
            )
        )
        upload_transaction_keys.add(transaction_key)
        transactions_inserted += 1
        affected_customer_ids.add(customer_id)

    db.commit()

    # Single batch recompute for the whole project, not once per row — see
    # docs/architecture/CSV-Upload-Flow.md for why.
    if affected_customer_ids:
        analytics_service.recompute_project_segments(db, project_id)

    return UploadResult(
        customers_created=customers_created,
        transactions_inserted=transactions_inserted,
        rows_skipped=rows_skipped,
        errors=errors,
    )
