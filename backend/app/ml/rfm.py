"""
Computes Recency, Frequency, and Monetary (RFM) values for customers from
their Transactions. RFM is always calculated on demand from live data,
never stored — see docs/architecture/Database-Schema.md for the reasoning.
"""
import uuid
from datetime import date
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Transaction, Customer


def calculate_customer_rfm(
    db: Session,
    customer_id: uuid.UUID,
    reference_date: Optional[date] = None,
) -> Optional[dict]:
    """
    Computes RFM for a single customer.

    Returns None if the customer has no transactions yet — RFM is
    undefined for a customer with zero purchase history, and callers
    should treat that as "not yet segmentable" rather than "recency 0."
    """
    reference_date = reference_date or date.today()

    result = (
        db.query(
            func.max(Transaction.order_date).label("last_order_date"),
            func.count(Transaction.id).label("frequency"),
            func.sum(Transaction.order_amount).label("monetary"),
        )
        .filter(Transaction.customer_id == customer_id)
        .first()
    )

    if result is None or result.last_order_date is None:
        return None

    return {
        "customer_id": customer_id,
        "recency_days": (reference_date - result.last_order_date).days,
        "frequency_count": result.frequency,
        "monetary_value": float(result.monetary),
    }


def calculate_project_rfm(
    db: Session,
    project_id: uuid.UUID,
    reference_date: Optional[date] = None,
) -> list[dict]:
    """
    Computes RFM for every customer in a project that has at least one
    transaction, in a single grouped query. This is the input K-Means
    clustering will consume — customers with no transactions are
    naturally excluded by the inner join, since they can't be segmented
    yet.
    """
    reference_date = reference_date or date.today()

    rows = (
        db.query(
            Transaction.customer_id,
            func.max(Transaction.order_date).label("last_order_date"),
            func.count(Transaction.id).label("frequency"),
            func.sum(Transaction.order_amount).label("monetary"),
        )
        .join(Customer, Transaction.customer_id == Customer.id)
        .filter(Customer.project_id == project_id)
        .group_by(Transaction.customer_id)
        .all()
    )

    return [
        {
            "customer_id": row.customer_id,
            "recency_days": (reference_date - row.last_order_date).days,
            "frequency_count": row.frequency,
            "monetary_value": float(row.monetary),
        }
        for row in rows
    ]
