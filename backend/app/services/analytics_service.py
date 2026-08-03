"""
Orchestrates app/ml/* to recompute RFM + segment for every customer in a
project, writes the result to Segments, and logs to Segment_History when
a customer's segment label actually changes. This is the piece that
connects the pure ML functions (rfm.py, clustering.py, labeling.py) to the
live database — nothing in app/ml/ touches the database directly.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database.models import Customer, Segment, SegmentHistory
from app.ml.rfm import calculate_project_rfm
from app.ml.clustering import cluster_customers
from app.ml.labeling import label_clusters


def recompute_project_segments(db: Session, project_id: uuid.UUID) -> dict[uuid.UUID, str]:
    """
    Recomputes RFM, re-clusters, and re-labels every customer in a
    project, then upserts Segments and logs any label changes to
    Segment_History.

    This always operates on the whole project, never a single customer in
    isolation — K-Means cluster assignments are relative to the current
    customer base as a whole, so one new transaction can shift what
    "high value" means for everyone else in the same project too.

    Returns {customer_id: new_segment_name} for every customer with
    enough transaction history to be segmented. Customers with zero
    transactions are silently skipped (same behavior as
    calculate_project_rfm), and returns {} if there's nothing to segment
    yet (e.g. a brand-new project with no transactions at all).
    """
    rfm_records = calculate_project_rfm(db, project_id)
    if not rfm_records:
        return {}

    cluster_assignment = cluster_customers(rfm_records)
    if not cluster_assignment:
        return {}

    cluster_labels = label_clusters(rfm_records, cluster_assignment)

    results: dict[uuid.UUID, str] = {}

    for record in rfm_records:
        customer_id = record["customer_id"]
        cluster_number = cluster_assignment.get(customer_id)
        if cluster_number is None:
            continue

        new_segment_name = cluster_labels.get(cluster_number)
        if new_segment_name is None:
            continue

        existing_segment = (
            db.query(Segment)
            .filter(Segment.customer_id == customer_id)
            .first()
        )
        old_segment_name = existing_segment.segment_name if existing_segment else None

        if existing_segment:
            existing_segment.cluster_number = cluster_number
            existing_segment.segment_name = new_segment_name
            # generated_at only has a server_default (applies on INSERT),
            # not onupdate, so it has to be bumped explicitly here to
            # reflect "when this was last recomputed."
            existing_segment.generated_at = datetime.now(timezone.utc)
        else:
            db.add(
                Segment(
                    project_id=project_id,
                    customer_id=customer_id,
                    cluster_number=cluster_number,
                    segment_name=new_segment_name,
                )
            )

        if old_segment_name != new_segment_name:
            db.add(
                SegmentHistory(
                    customer_id=customer_id,
                    old_segment=old_segment_name,
                    new_segment=new_segment_name,
                )
            )

        results[customer_id] = new_segment_name

    db.commit()
    return results


def recompute_for_customer(db: Session, customer_id: uuid.UUID) -> dict[uuid.UUID, str]:
    """
    Convenience wrapper for the common case: a single transaction changed
    for one customer. Looks up which project that customer belongs to and
    recomputes the whole project (see recompute_project_segments for why
    it can't be scoped to just one customer). Returns {} if the customer
    doesn't exist — callers shouldn't treat that as an error, since it
    just means there's nothing to recompute.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {}
    return recompute_project_segments(db, customer.project_id)


def list_project_segments(db: Session, project_id: uuid.UUID) -> list[Segment]:
    """All current Segment rows for a project (one per segmented customer)."""
    return db.query(Segment).filter(Segment.project_id == project_id).all()


def get_customer_segment(db: Session, customer_id: uuid.UUID) -> Segment | None:
    """The current Segment row for one customer, or None if not segmented yet."""
    return db.query(Segment).filter(Segment.customer_id == customer_id).first()


def list_recent_migrations(db: Session, project_id: uuid.UUID, limit: int = 20) -> list[SegmentHistory]:
    """
    Recent segment changes across a project, most recent first — powers
    the "customer moved from At Risk to Loyal" live feed on the dashboard.
    """
    return (
        db.query(SegmentHistory)
        .join(Customer, SegmentHistory.customer_id == Customer.id)
        .filter(Customer.project_id == project_id)
        .order_by(SegmentHistory.changed_at.desc())
        .limit(limit)
        .all()
    )
