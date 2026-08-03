"""
Dashboard aggregation logic: total customers, total revenue, segment
breakdown for a project. Backs GET /projects/{project_id}/dashboard/overview.
"""
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Customer, Transaction
from app.analytics.revenue import revenue_by_segment


def get_dashboard_overview(db: Session, project_id: uuid.UUID) -> dict:
    """
    total_customers and total_revenue cover the whole project (every
    customer and transaction), regardless of segmentation status.
    segment_breakdown, by contrast, only covers segmented customers (see
    revenue_by_segment) — so it's normal for these two revenue figures to
    differ slightly if a brand-new customer hasn't been segmented yet.
    """
    total_customers = (
        db.query(func.count(Customer.id))
        .filter(Customer.project_id == project_id)
        .scalar()
    ) or 0

    total_revenue = (
        db.query(func.coalesce(func.sum(Transaction.order_amount), 0))
        .join(Customer, Transaction.customer_id == Customer.id)
        .filter(Customer.project_id == project_id)
        .scalar()
    ) or 0

    return {
        "total_customers": total_customers,
        "total_revenue": float(total_revenue),
        "segment_breakdown": revenue_by_segment(db, project_id),
    }
