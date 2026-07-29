"""
Tests for RFM calculation. Uses an in-memory SQLite database (same pattern
as test_transaction_authorization.py) so these run instantly with no real
Postgres connection needed.
"""
import uuid
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.models import Project, Customer, Transaction
from app.ml.rfm import calculate_customer_rfm, calculate_project_rfm


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


def test_customer_with_no_transactions_returns_none(db, project):
    customer = make_customer(db, project.id, "empty@example.com")

    result = calculate_customer_rfm(db, customer.id, reference_date=date(2026, 8, 1))

    assert result is None


def test_customer_rfm_math_is_correct(db, project):
    customer = make_customer(db, project.id, "ali@example.com")
    make_transaction(db, customer.id, date(2026, 7, 1), "50.00")
    make_transaction(db, customer.id, date(2026, 7, 20), "100.00")
    make_transaction(db, customer.id, date(2026, 7, 25), "75.50")

    result = calculate_customer_rfm(db, customer.id, reference_date=date(2026, 8, 1))

    assert result["frequency_count"] == 3
    assert result["monetary_value"] == pytest.approx(225.50)
    # Most recent order was Jul 25; reference date Aug 1 -> 7 days
    assert result["recency_days"] == 7


def test_project_rfm_excludes_customers_with_no_transactions(db, project):
    active_customer = make_customer(db, project.id, "active@example.com")
    make_transaction(db, active_customer.id, date(2026, 7, 15), "40.00")

    make_customer(db, project.id, "inactive@example.com")  # never buys

    results = calculate_project_rfm(db, project.id, reference_date=date(2026, 8, 1))

    assert len(results) == 1
    assert results[0]["customer_id"] == active_customer.id


def test_project_rfm_covers_multiple_customers_independently(db, project):
    customer_a = make_customer(db, project.id, "a@example.com")
    make_transaction(db, customer_a.id, date(2026, 7, 1), "10.00")
    make_transaction(db, customer_a.id, date(2026, 7, 2), "10.00")

    customer_b = make_customer(db, project.id, "b@example.com")
    make_transaction(db, customer_b.id, date(2026, 7, 30), "500.00")

    results = {r["customer_id"]: r for r in calculate_project_rfm(db, project.id, reference_date=date(2026, 8, 1))}

    assert results[customer_a.id]["frequency_count"] == 2
    assert results[customer_a.id]["monetary_value"] == pytest.approx(20.00)

    assert results[customer_b.id]["frequency_count"] == 1
    assert results[customer_b.id]["monetary_value"] == pytest.approx(500.00)
    assert results[customer_b.id]["recency_days"] == 2
