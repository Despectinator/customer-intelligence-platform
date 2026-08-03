"""
End-to-end tests for the CSV upload endpoint, through actual HTTP
requests. Same StaticPool pattern as test_analytics_endpoints.py — see
that file for why StaticPool matters with FastAPI's threaded sync routes.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.database.models import Customer, Transaction
from app.core.security import get_current_user, CurrentUser
from app.api.dependencies import get_db as api_get_db, get_current_user as api_get_current_user


@pytest.fixture()
def test_db():
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


@pytest.fixture(autouse=True)
def clear_overrides_after_test():
    yield
    app.dependency_overrides.clear()


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


def _upload(client, project_id, csv_text, filename="import.csv"):
    return client.post(
        f"/projects/{project_id}/transactions/upload-csv",
        files={"file": (filename, csv_text, "text/csv")},
    )


def test_valid_csv_creates_customers_and_transactions(test_db):
    user_id = uuid.uuid4()
    client = _client_as(test_db, user_id)
    project = client.post("/projects", json={"name": "Store", "description": ""}).json()

    csv_text = (
        "first_name,last_name,email,phone,company,order_date,order_amount,payment_method\n"
        "Ali,Khan,ali@example.com,0300,DemoCo,2026-07-20,500,card\n"
        "Ali,Khan,ali@example.com,0300,DemoCo,2026-07-25,700,card\n"
        "Sara,Malik,sara@example.com,,,2026-07-01,150,cash\n"
    )

    response = _upload(client, project["id"], csv_text)

    assert response.status_code == 200
    body = response.json()
    assert body["customers_created"] == 2  # Ali and Sara, not 3 (Ali appears twice)
    assert body["transactions_inserted"] == 3
    assert body["rows_skipped"] == 0
    assert body["errors"] == []

    customers = test_db.query(Customer).filter(Customer.project_id == uuid.UUID(project["id"])).all()
    assert len(customers) == 2
    transactions = test_db.query(Transaction).all()
    assert len(transactions) == 3


def test_invalid_rows_are_skipped_not_fatal(test_db):
    user_id = uuid.uuid4()
    client = _client_as(test_db, user_id)
    project = client.post("/projects", json={"name": "Store", "description": ""}).json()

    csv_text = (
        "first_name,last_name,email,phone,company,order_date,order_amount,payment_method\n"
        "Ali,Khan,ali@example.com,,,2026-07-20,500,card\n"
        "Bad,Row,bad@example.com,,,not-a-date,500,card\n"
        "Bad,Amount,badamount@example.com,,,2026-07-20,not-a-number,card\n"
        "Bad,Negative,neg@example.com,,,2026-07-20,-50,card\n"
        ",,missingname@example.com,,,2026-07-20,50,card\n"
    )

    response = _upload(client, project["id"], csv_text)

    assert response.status_code == 200
    body = response.json()
    assert body["transactions_inserted"] == 1  # only Ali's row was valid
    assert body["rows_skipped"] == 4
    assert len(body["errors"]) == 4
    # Row numbers should point at actual CSV rows (header = row 1)
    error_rows = {e["row"] for e in body["errors"]}
    assert error_rows == {3, 4, 5, 6}


def test_missing_required_columns_rejected_immediately(test_db):
    user_id = uuid.uuid4()
    client = _client_as(test_db, user_id)
    project = client.post("/projects", json={"name": "Store", "description": ""}).json()

    csv_text = "first_name,last_name\nAli,Khan\n"  # missing email, order_date, order_amount

    response = _upload(client, project["id"], csv_text)

    assert response.status_code == 400
    body = response.json()
    assert "Missing required column" in body["detail"]


def test_non_csv_file_rejected(test_db):
    user_id = uuid.uuid4()
    client = _client_as(test_db, user_id)
    project = client.post("/projects", json={"name": "Store", "description": ""}).json()

    response = _upload(client, project["id"], "not a csv", filename="notes.txt")

    assert response.status_code == 400


def test_upload_triggers_recompute(test_db):
    user_id = uuid.uuid4()
    client = _client_as(test_db, user_id)
    project = client.post("/projects", json={"name": "Store", "description": ""}).json()

    csv_text = (
        "first_name,last_name,email,phone,company,order_date,order_amount,payment_method\n"
        "Ali,Khan,ali@example.com,,,2026-07-27,1800,card\n"
        "Sara,Malik,sara@example.com,,,2026-02-01,1600,card\n"
        "Bilal,Hussain,bilal@example.com,,,2026-01-01,40,card\n"
        "Zara,Ahmed,zara@example.com,,,2026-07-28,50,card\n"
    )
    _upload(client, project["id"], csv_text)

    segments_resp = client.get(f"/projects/{project['id']}/segments")
    assert segments_resp.status_code == 200
    segments = segments_resp.json()
    assert len(segments) == 4  # recompute ran automatically after the upload


def test_upload_requires_project_ownership(test_db):
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    client_a = _client_as(test_db, user_a)
    project = client_a.post("/projects", json={"name": "Store", "description": ""}).json()

    client_b = _client_as(test_db, user_b)
    response = _upload(client_b, project["id"], "first_name,last_name,email,order_date,order_amount\n")

    assert response.status_code == 404


def test_upload_to_nonexistent_project_returns_404_not_500(test_db):
    user_id = uuid.uuid4()
    client = _client_as(test_db, user_id)

    nonexistent_project_id = "11111111-1111-1111-1111-111111111111"
    csv_text = (
        "first_name,last_name,email,phone,company,order_date,order_amount,payment_method\n"
        "Ali,Khan,ali@example.com,,,2026-07-20,500,card\n"
    )

    response = _upload(client, nonexistent_project_id, csv_text)

    assert response.status_code == 404


def test_invalid_email_format_is_skipped_not_500(test_db):
    user_id = uuid.uuid4()
    client = _client_as(test_db, user_id)
    project = client.post("/projects", json={"name": "Store", "description": ""}).json()

    csv_text = (
        "first_name,last_name,email,order_date,order_amount\n"
        "Ali,Khan,not-an-email,2026-07-20,500\n"
        "Sara,Malik,sara@example.com,2026-07-20,150\n"
    )

    response = _upload(client, project["id"], csv_text)

    assert response.status_code == 200
    body = response.json()
    assert body["customers_created"] == 1  # only Sara, Ali's row was rejected
    assert body["transactions_inserted"] == 1
    assert body["rows_skipped"] == 1
    assert "not valid" in body["errors"][0]["reason"]
