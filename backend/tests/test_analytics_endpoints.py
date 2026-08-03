"""
End-to-end tests for the analytics/dashboard endpoints, going through
actual HTTP requests (not calling service functions directly), using the
same in-memory SQLite + dependency-override pattern as
test_transaction_authorization.py.
"""
import uuid
from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.database.models import Project, Customer, Transaction
from app.core.security import get_current_user, CurrentUser
from app.api.dependencies import get_db as api_get_db, get_current_user as api_get_current_user


@pytest.fixture()
def test_db():
    # StaticPool matters here: FastAPI runs sync route handlers in a
    # worker thread via anyio's threadpool, but SQLAlchemy's default
    # pooling for sqlite:///:memory: is thread-local — meaning the thread
    # that creates the tables and the thread that later handles the HTTP
    # request can silently end up with two separate, empty in-memory
    # databases. StaticPool forces a single shared connection regardless
    # of which thread uses it.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _client_as(test_db, user_id):
    def override_get_db():
        yield test_db

    def override_get_current_user():
        return CurrentUser(id=user_id, email=f"{user_id}@example.com")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[api_get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[api_get_current_user] = override_get_current_user

    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_overrides_after_test():
    yield
    app.dependency_overrides.clear()


def _seed_project_with_customers(test_db, user_id):
    project = Project(user_id=user_id, name="Test Store")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    loyal = Customer(project_id=project.id, first_name="Loyal", last_name="Customer", email="loyal@example.com")
    at_risk = Customer(project_id=project.id, first_name="AtRisk", last_name="Customer", email="atrisk@example.com")
    lost = Customer(project_id=project.id, first_name="Lost", last_name="Customer", email="lost@example.com")
    new = Customer(project_id=project.id, first_name="New", last_name="Customer", email="new@example.com")
    test_db.add_all([loyal, at_risk, lost, new])
    test_db.commit()
    for c in (loyal, at_risk, lost, new):
        test_db.refresh(c)

    test_db.add_all([
        Transaction(customer_id=loyal.id, order_date=date(2026, 7, 27), order_amount="1800.00"),
        Transaction(customer_id=at_risk.id, order_date=date(2026, 2, 1), order_amount="1600.00"),
        Transaction(customer_id=lost.id, order_date=date(2026, 1, 1), order_amount="40.00"),
        Transaction(customer_id=new.id, order_date=date(2026, 7, 28), order_amount="50.00"),
    ])
    test_db.commit()

    return project, {"loyal": loyal, "at_risk": at_risk, "lost": lost, "new": new}


def test_recompute_endpoint_creates_segments(test_db):
    user_id = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_id)
    client = _client_as(test_db, user_id)

    response = client.post(f"/projects/{project.id}/segments/recompute")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    segment_names = {row["segment_name"] for row in body}
    assert segment_names == {"Loyal High-Value", "At Risk", "Lost", "New"}
    # Every segment should carry a recommendation string
    assert all(row["recommendation"] for row in body)


def test_list_segments_reflects_recompute(test_db):
    user_id = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_id)
    client = _client_as(test_db, user_id)

    client.post(f"/projects/{project.id}/segments/recompute")
    response = client.get(f"/projects/{project.id}/segments")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_customer_segment_endpoint(test_db):
    user_id = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_id)
    client = _client_as(test_db, user_id)

    client.post(f"/projects/{project.id}/segments/recompute")
    response = client.get(f"/customers/{customers['loyal'].id}/segment")

    assert response.status_code == 200
    assert response.json()["segment_name"] == "Loyal High-Value"


def test_customer_segment_404_before_recompute(test_db):
    user_id = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_id)
    client = _client_as(test_db, user_id)

    # No recompute has run yet -> no Segment row exists
    response = client.get(f"/customers/{customers['loyal'].id}/segment")
    assert response.status_code == 404


def test_dashboard_overview(test_db):
    user_id = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_id)
    client = _client_as(test_db, user_id)

    client.post(f"/projects/{project.id}/segments/recompute")
    response = client.get(f"/projects/{project.id}/dashboard/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["total_customers"] == 4
    assert body["total_revenue"] == pytest.approx(3490.00)
    assert len(body["segment_breakdown"]) == 4
    percentages = [row["revenue_percentage"] for row in body["segment_breakdown"]]
    assert sum(percentages) == pytest.approx(100.0, abs=0.1)


def test_dashboard_migrations_lists_changes(test_db):
    user_id = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_id)
    client = _client_as(test_db, user_id)

    client.post(f"/projects/{project.id}/segments/recompute")
    response = client.get(f"/projects/{project.id}/dashboard/migrations")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4  # first-ever segment assignment counts as a migration (old_segment=null)
    assert all(row["new_segment"] for row in body)


def test_analytics_endpoints_require_auth(test_db):
    user_id = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_id)
    client = _client_as(test_db, user_id)
    # Wipe the auth override so this request is unauthenticated
    del app.dependency_overrides[get_current_user]
    del app.dependency_overrides[api_get_current_user]

    response = client.get(f"/projects/{project.id}/segments")
    assert response.status_code in (401, 403)


def test_user_b_cannot_see_user_a_project_segments(test_db):
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    project, customers = _seed_project_with_customers(test_db, user_a)

    client_a = _client_as(test_db, user_a)
    client_a.post(f"/projects/{project.id}/segments/recompute")

    client_b = _client_as(test_db, user_b)
    response = client_b.get(f"/projects/{project.id}/segments")
    assert response.status_code == 404
