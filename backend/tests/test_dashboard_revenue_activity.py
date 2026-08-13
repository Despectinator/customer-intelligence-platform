"""Endpoint tests for dashboard revenue and recent activity."""
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user as api_get_current_user
from app.api.dependencies import get_db as api_get_db
from app.core.security import CurrentUser, get_current_user
from app.database.database import Base, get_db
from app.database.models import Customer, Project, Transaction
from app.main import app


@pytest.fixture()
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clear_overrides_after_test():
    yield
    app.dependency_overrides.clear()


def client_as(test_db, user_id):
    def override_get_db():
        yield test_db

    def override_get_current_user():
        return CurrentUser(id=user_id, email=f"{user_id}@example.com")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[api_get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[api_get_current_user] = override_get_current_user
    return TestClient(app)


def seed_project(db, user_id):
    project = Project(user_id=user_id, name="Test Store")
    db.add(project)
    db.commit()
    db.refresh(project)

    ali = Customer(
        project_id=project.id,
        first_name="Ali",
        last_name="Khan",
        email="ali@example.com",
    )
    sara = Customer(
        project_id=project.id,
        first_name="Sara",
        last_name="Malik",
        email="sara@example.com",
    )
    db.add_all([ali, sara])
    db.commit()
    db.refresh(ali)
    db.refresh(sara)
    db.add_all(
        [
            Transaction(customer_id=ali.id, order_date=date(2026, 7, 20), order_amount="500.00"),
            Transaction(customer_id=ali.id, order_date=date(2026, 7, 20), order_amount="300.00"),
            Transaction(customer_id=sara.id, order_date=date(2026, 7, 21), order_amount="150.00"),
        ]
    )
    db.commit()
    return project


def test_revenue_groups_and_sums_transactions_by_date(test_db):
    user_id = uuid.uuid4()
    project = seed_project(test_db, user_id)

    response = client_as(test_db, user_id).get(
        f"/projects/{project.id}/dashboard/revenue"
    )

    assert response.status_code == 200
    by_date = {row["date"]: row["revenue"] for row in response.json()}
    assert by_date["2026-07-20"] == pytest.approx(800.0)
    assert by_date["2026-07-21"] == pytest.approx(150.0)


def test_revenue_is_ordered_by_date(test_db):
    user_id = uuid.uuid4()
    project = seed_project(test_db, user_id)

    response = client_as(test_db, user_id).get(
        f"/projects/{project.id}/dashboard/revenue"
    )

    dates = [row["date"] for row in response.json()]
    assert dates == sorted(dates)


def test_revenue_empty_project_returns_empty_list(test_db):
    user_id = uuid.uuid4()
    project = Project(user_id=user_id, name="Empty Store")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    response = client_as(test_db, user_id).get(
        f"/projects/{project.id}/dashboard/revenue"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_revenue_requires_project_ownership(test_db):
    owner_id = uuid.uuid4()
    project = seed_project(test_db, owner_id)

    response = client_as(test_db, uuid.uuid4()).get(
        f"/projects/{project.id}/dashboard/revenue"
    )

    assert response.status_code == 404


def test_activity_returns_recent_transactions_first(test_db):
    user_id = uuid.uuid4()
    project = seed_project(test_db, user_id)

    response = client_as(test_db, user_id).get(
        f"/projects/{project.id}/dashboard/activity"
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert body[0]["date"] == "2026-07-21"


def test_activity_label_includes_customer_name_and_amount(test_db):
    user_id = uuid.uuid4()
    project = seed_project(test_db, user_id)

    body = client_as(test_db, user_id).get(
        f"/projects/{project.id}/dashboard/activity"
    ).json()

    assert any("Sara Malik" in row["label"] for row in body)
    assert any("150.00" in row["label"] for row in body)


def test_activity_default_limit_is_ten(test_db):
    user_id = uuid.uuid4()
    project = Project(user_id=user_id, name="Busy Store")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    customer = Customer(
        project_id=project.id,
        first_name="Busy",
        last_name="Customer",
        email="busy@example.com",
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)

    for day in range(1, 16):
        test_db.add(
            Transaction(
                customer_id=customer.id,
                order_date=date(2026, 7, day),
                order_amount="10.00",
            )
        )
    test_db.commit()

    body = client_as(test_db, user_id).get(
        f"/projects/{project.id}/dashboard/activity"
    ).json()
    assert len(body) == 10


def test_activity_requires_project_ownership(test_db):
    owner_id = uuid.uuid4()
    project = seed_project(test_db, owner_id)

    response = client_as(test_db, uuid.uuid4()).get(
        f"/projects/{project.id}/dashboard/activity"
    )

    assert response.status_code == 404


def test_activity_requires_authentication(test_db):
    owner_id = uuid.uuid4()
    project = seed_project(test_db, owner_id)
    client = client_as(test_db, owner_id)
    del app.dependency_overrides[get_current_user]
    del app.dependency_overrides[api_get_current_user]

    response = client.get(f"/projects/{project.id}/dashboard/activity")

    assert response.status_code in (401, 403)
