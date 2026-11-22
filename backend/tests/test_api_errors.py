"""Tests for the stable API error envelope and request correlation IDs."""

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_not_found_uses_safe_error_envelope_and_request_id():
    response = client.get("/route-that-does-not-exist")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "not_found"
    assert payload["error"]["message"]
    assert payload["error"]["request_id"] == response.headers["X-Request-ID"]


def test_validation_errors_do_not_echo_submitted_values():
    response = client.post("/api/v1/chat", json={"question": ""})

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed"
    assert payload["error"]["request_id"] == response.headers["X-Request-ID"]
    assert '""' not in response.text
