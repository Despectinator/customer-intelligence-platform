from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_allowed_origin_gets_cors_headers():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_disallowed_origin_does_not_get_cors_headers():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://evil-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") is None
