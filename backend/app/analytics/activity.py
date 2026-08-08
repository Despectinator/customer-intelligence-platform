"""
Recent dashboard activity.

Builds recent transaction activity for a project.
"""

import uuid

from sqlalchemy.orm import Session

from app.database.models import Customer, Transaction


def get_recent_activity(
    db: Session,
    project_id: uuid.UUID,
    limit: int = 10,
) -> list[dict]:
    """
    Return the most recent transactions for a project.

    Each activity contains:
    - transaction id
    - customer name
    - transaction date
    - transaction amount
    - payment method
    - status
    """

    rows = (
        db.query(Transaction, Customer)
        .join(Customer, Transaction.customer_id == Customer.id)
        .filter(Customer.project_id == project_id)
        .order_by(Transaction.order_date.desc(), Transaction.created_at.desc())
        .limit(limit)
        .all()
    )

    activities = []

    for transaction, customer in rows:
        customer_name = f"{customer.first_name} {customer.last_name}".strip()

        activities.append(
            {
                "id": transaction.id,
                "label": (
                    f"{customer_name} made a purchase of "
                    f"₨{float(transaction.order_amount):,.2f}"
                ),
                "date": transaction.order_date,
                "status": "Completed",
            }
        )

    return activities
