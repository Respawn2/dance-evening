"""System endpoints behaviour."""

from fastapi.testclient import TestClient

from evenings.api.middleware import REQUEST_ID_HEADER


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_require_configuration_of_dependencies(client: TestClient) -> None:
    """Liveness must answer even though no database is reachable in tests."""
    assert client.get("/health").status_code == 200


def test_version_reports_configured_version(client: TestClient) -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "0.0.0-test", "environment": "test"}


def test_request_id_is_returned(client: TestClient) -> None:
    response = client.get("/health")

    assert response.headers[REQUEST_ID_HEADER]


def test_incoming_request_id_is_preserved(client: TestClient) -> None:
    """A request id coming from a caller must be reused, not replaced."""
    given = "11111111-2222-3333-4444-555555555555"

    response = client.get("/health", headers={REQUEST_ID_HEADER: given})

    assert response.headers[REQUEST_ID_HEADER] == given


def test_unknown_path_returns_404(client: TestClient) -> None:
    assert client.get("/nope").status_code == 404
