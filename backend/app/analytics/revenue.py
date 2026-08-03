"""
Revenue-by-segment calculations. Backs the revenue breakdown shown on the
analytics dashboard and the /segments/summary endpoint.
"""
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Segment, Customer, Transaction


def revenue_by_segment(db: Session, project_id: uuid.UUID) -> list[dict]:
    """
    Returns one row per segment_name currently present in the project:
    {segment_name, customer_count, revenue_total, revenue_percentage}.

    revenue_total sums every transaction belonging to customers in that
    segment. revenue_percentage is each segment's share of the project's
    total revenue across all *segmented* customers — customers with no
    segment yet (e.g. brand new, zero transactions) are naturally
    excluded, since they have nothing to contribute either way.
    """
    rows = (
        db.query(
            Segment.segment_name,
            func.count(func.distinct(Segment.customer_id)).label("customer_count"),
            func.coalesce(func.sum(Transaction.order_amount), 0).label("revenue_total"),
        )
        .join(Customer, Segment.customer_id == Customer.id)
        .outerjoin(Transaction, Transaction.customer_id == Customer.id)
        .filter(Segment.project_id == project_id)
        .group_by(Segment.segment_name)
        .all()
    )

    total_revenue = sum(float(row.revenue_total) for row in rows)

    return [
        {
            "segment_name": row.segment_name,
            "customer_count": row.customer_count,
            "revenue_total": float(row.revenue_total),
            "revenue_percentage": (
                round(float(row.revenue_total) / total_revenue * 100, 2) if total_revenue > 0 else 0.0
            ),
        }
        for row in rows
    ]
