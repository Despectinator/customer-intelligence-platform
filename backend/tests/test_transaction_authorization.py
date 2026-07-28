"""
Integration test for the authorization fix on Transaction endpoints.

This test creates two separate users against an in-memory SQLite database
(via dependency overrides — no real Supabase account or live Postgres
needed) and verifies that User B cannot read User A's customer's
transactions. This is the direct regression test for the IDOR
vulnerability fixed on Day 7: the endpoints previously required a valid
login, but never checked that the logged-in user actually owned the
customer being accessed.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.database.models import Project, Customer, Transaction
from app.core.security import get_current_user, CurrentUser
from app.api.dependencies import get_db as api_get_db, get_current_user as api_get_current_user


@pytest.fixture()
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def user_a_id():
    return uuid.uuid4()


@pytest.fixture()
def user_b_id():
    return uuid.uuid4()


@pytest.fixture()
def seeded_customer_id(test_db, user_a_id):
    """User A's project, with one customer in it."""
    project = Project(user_id=user_a_id, name="User A's Store")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    customer = Customer(
        project_id=project.id,
        first_name="Ali",
        last_name="Bokhari",
        email="ali@example.com",
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)

    return customer.id


def _client_as(test_db, user_id):
    """Builds a TestClient authenticated as a specific fake user, backed
    by the shared in-memory test database, bypassing real Supabase auth
    and the real Postgres connection entirely."""

    def override_get_db():
        yield test_db

    def override_get_current_user():
        return CurrentUser(id=user_id, email=f"{user_id}@example.com")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[api_get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[api_get_current_user] = override_get_current_user

    return TestClient(app)


def test_user_b_cannot_read_user_a_customer_transactions(test_db, user_a_id, user_b_id, seeded_customer_id):
    client_b = _client_as(test_db, user_b_id)

    response = client_b.get(f"/customers/{seeded_customer_id}/transactions")

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_user_b_cannot_create_transaction_for_user_a_customer(test_db, user_a_id, user_b_id, seeded_customer_id):
    client_b = _client_as(test_db, user_b_id)

    response = client_b.post(
        f"/customers/{seeded_customer_id}/transactions",
        json={"order_date": "2026-07-20", "order_amount": "50.00", "payment_method": "card"},
    )

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_user_a_can_read_their_own_customer_transactions(test_db, user_a_id, seeded_customer_id):
    client_a = _client_as(test_db, user_a_id)

    response = client_a.get(f"/customers/{seeded_customer_id}/transactions")

    assert response.status_code == 200
    app.dependency_overrides.clear()
