"""
Dashboard aggregation logic: total customers, total revenue, segment
breakdown for a project. Backs GET /projects/{project_id}/dashboard/overview.
"""
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Customer, Transaction
from app.analytics.revenue import revenue_by_segment
from app.ml.clustering import MIN_CUSTOMERS_FOR_SEGMENTATION
from app.ml.rfm import calculate_project_rfm


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

    total_transactions = (
        db.query(func.count(Transaction.id))
        .join(Customer, Transaction.customer_id == Customer.id)
        .filter(Customer.project_id == project_id)
        .scalar()
    ) or 0

    segmentable_customer_count = len(calculate_project_rfm(db, project_id))
    enough_data_for_segmentation = (
        segmentable_customer_count >= MIN_CUSTOMERS_FOR_SEGMENTATION
    )

    segment_breakdown = (
        revenue_by_segment(db, project_id)
        if enough_data_for_segmentation
        else []
    )

    if total_customers == 0:
        segmentation_status = "no_data"
        segmentation_message = "No customer data yet."
    elif total_transactions == 0:
        segmentation_status = "no_transactions"
        segmentation_message = "No transactions yet."
    elif not enough_data_for_segmentation:
        segmentation_status = "insufficient_data"
        segmentation_message = (
            "At least "
            f"{MIN_CUSTOMERS_FOR_SEGMENTATION} customers with transaction "
            "history are required for segmentation."
        )
    elif not segment_breakdown:
        segmentation_status = "not_generated"
        segmentation_message = "Run segmentation to generate customer segments."
    else:
        segmentation_status = "ready"
        segmentation_message = "Segmentation is available."

    return {
        "total_customers": total_customers,
        "total_revenue": float(total_revenue),
        "total_transactions": total_transactions,
        "segmentable_customers": segmentable_customer_count,
        "segment_breakdown": segment_breakdown,
        "segmentation_status": segmentation_status,
        "segmentation_message": segmentation_message,
    }
