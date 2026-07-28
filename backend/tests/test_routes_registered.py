from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_expected_paths_are_registered():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]

    expected = [
        "/health",
        "/projects",
        "/projects/{project_id}",
        "/projects/{project_id}/customers",
        "/projects/{project_id}/customers/{customer_id}",
        "/customers/{customer_id}/transactions",
        "/customers/{customer_id}/transactions/{transaction_id}",
    ]
    for path in expected:
        assert path in paths, f"Expected route {path} is not registered"


def test_protected_routes_require_auth():
    response = client.get("/projects")
    assert response.status_code in (401, 403)


def test_transactions_require_auth_not_just_a_valid_customer_id():
    # Regression test for the IDOR bug fixed today: hitting a transactions
    # endpoint with no token must fail with 401, not leak data for an
    # arbitrary customer_id.
    fake_customer_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/customers/{fake_customer_id}/transactions")
    assert response.status_code in (401, 403)
