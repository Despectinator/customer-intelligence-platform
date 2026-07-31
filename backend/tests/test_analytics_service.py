"""
Tests for analytics_service.py — the orchestration layer that connects
RFM/clustering/labeling (pure functions, tested separately in test_rfm.py,
test_clustering.py, test_labeling.py) to the live database.
"""
import uuid
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.models import Project, Customer, Transaction, Segment, SegmentHistory
from app.services import analytics_service


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def project(db):
    p = Project(user_id=uuid.uuid4(), name="Test Store")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def make_customer(db, project_id, email):
    c = Customer(project_id=project_id, first_name="Test", last_name="Customer", email=email)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def make_transaction(db, customer_id, order_date, amount):
    t = Transaction(customer_id=customer_id, order_date=order_date, order_amount=amount)
    db.add(t)
    db.commit()
    return t


def test_recompute_with_no_customers_returns_empty(db, project):
    result = analytics_service.recompute_project_segments(db, project.id)
    assert result == {}


def test_recompute_creates_segment_rows(db, project):
    customer_a = make_customer(db, project.id, "a@example.com")
    make_transaction(db, customer_a.id, date(2026, 7, 1), "1500.00")
    make_transaction(db, customer_a.id, date(2026, 7, 25), "1200.00")

    customer_b = make_customer(db, project.id, "b@example.com")
    make_transaction(db, customer_b.id, date(2026, 1, 1), "20.00")

    result = analytics_service.recompute_project_segments(db, project.id)

    assert customer_a.id in result
    assert customer_b.id in result

    segments = db.query(Segment).filter(Segment.project_id == project.id).all()
    assert len(segments) == 2


def test_recompute_for_customer_finds_the_right_project(db, project):
    customer = make_customer(db, project.id, "solo@example.com")
    make_transaction(db, customer.id, date(2026, 7, 20), "80.00")

    # Only one customer -> cluster_customers() returns {} (fewer than 2
    # records), so this should resolve to {} rather than error.
    result = analytics_service.recompute_for_customer(db, customer.id)
    assert result == {}


def test_recompute_for_nonexistent_customer_returns_empty(db):
    result = analytics_service.recompute_for_customer(db, uuid.uuid4())
    assert result == {}


def test_segment_history_logs_only_on_actual_label_change(db, project):
    customer_a = make_customer(db, project.id, "a@example.com")
    make_transaction(db, customer_a.id, date(2026, 7, 1), "10.00")

    customer_b = make_customer(db, project.id, "b@example.com")
    make_transaction(db, customer_b.id, date(2026, 1, 1), "15.00")

    # First recompute: both customers are new to Segments -> each gets one
    # Segment_History row (old_segment=None -> new_segment=<label>).
    analytics_service.recompute_project_segments(db, project.id)
    history_after_first_run = db.query(SegmentHistory).all()
    assert len(history_after_first_run) == 2

    # Second recompute with identical data: nothing should have changed,
    # so no new history rows should be added.
    analytics_service.recompute_project_segments(db, project.id)
    history_after_second_run = db.query(SegmentHistory).all()
    assert len(history_after_second_run) == 2


def test_segment_history_logs_a_real_migration(db, project):
    # Four stable "anchor" customers, one per canonical archetype, plus
    # one "watched" customer whose history changes mid-test. Using 5
    # customers total (not 2) matters here: with fewer customers than
    # KMEANS_N_CLUSTERS, cluster_customers() clamps down and coarsens the
    # available labels (see the known limitation noted in clustering.py),
    # which would make a real "New -> Loyal High-Value" migration
    # untestable. Five customers keeps all four labels distinguishable.
    make_transaction(db, make_customer(db, project.id, "loyal@example.com").id, date(2026, 7, 27), "1800.00")
    make_transaction(db, make_customer(db, project.id, "atrisk@example.com").id, date(2026, 2, 1), "1600.00")
    make_transaction(db, make_customer(db, project.id, "lost@example.com").id, date(2026, 1, 1), "40.00")

    watched = make_customer(db, project.id, "watched@example.com")
    make_transaction(db, watched.id, date(2026, 7, 28), "50.00")  # starts out looking "New"

    analytics_service.recompute_project_segments(db, project.id)
    original_label = db.query(Segment).filter(Segment.customer_id == watched.id).first().segment_name
    assert original_label == "New"

    # Watched customer becomes a frequent high-value buyer, recency stays low.
    for _ in range(20):
        make_transaction(db, watched.id, date(2026, 7, 29), "500.00")

    analytics_service.recompute_project_segments(db, project.id)
    new_label = db.query(Segment).filter(Segment.customer_id == watched.id).first().segment_name
    assert new_label == "Loyal High-Value"

    migration_rows = (
        db.query(SegmentHistory)
        .filter(SegmentHistory.customer_id == watched.id, SegmentHistory.old_segment == "New")
        .all()
    )
    assert len(migration_rows) == 1
    assert migration_rows[0].new_segment == "Loyal High-Value"
