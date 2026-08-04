"""
Proves the global exception handler (app/exceptions/handlers.py) actually
does what it's for: HTTPException (401/404/etc, used throughout the real
routes) passes through completely untouched, while a genuine unhandled
bug gets caught, logged, and translated into a clean response that never
leaks internals to the client — except in DEBUG mode, where seeing the
real error is the point.
"""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.exceptions.handlers import register_exception_handlers


def _build_test_app(debug: bool):
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raises-http-exception")
    def raises_http_exception():
        raise HTTPException(status_code=404, detail="Not found, on purpose")

    @app.get("/raises-unexpected-bug")
    def raises_unexpected_bug():
        # Simulates a genuine, unanticipated bug — e.g. a KeyError deep in
        # some analytics code — not something already wrapped in an
        # HTTPException by the route/service layer.
        raise ValueError("something with a secret internal detail: db_password=hunter2")

    return app


def test_http_exception_passes_through_unchanged():
    app = _build_test_app(debug=False)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/raises-http-exception")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found, on purpose"}


def test_unhandled_exception_returns_generic_message_when_debug_false(monkeypatch):
    from app.exceptions import handlers as handlers_module
    monkeypatch.setattr(handlers_module.settings, "DEBUG", False)

    app = _build_test_app(debug=False)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/raises-unexpected-bug")

    assert response.status_code == 500
    body = response.json()
    assert body["success"] is False
    # The real point of this test: the secret must NOT leak to the client.
    assert "hunter2" not in body["message"]
    assert "db_password" not in body["message"]


def test_unhandled_exception_includes_detail_when_debug_true(monkeypatch):
    from app.exceptions import handlers as handlers_module
    monkeypatch.setattr(handlers_module.settings, "DEBUG", True)

    app = _build_test_app(debug=True)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/raises-unexpected-bug")

    assert response.status_code == 500
    body = response.json()
    assert body["success"] is False
    # In DEBUG mode, seeing the real error is the point.
    assert "ValueError" in body["message"]
