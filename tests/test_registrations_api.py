"""Behaviour of the registration scenario, recorded before refactoring."""

from fastapi.testclient import TestClient


def test_registration_is_created(client: TestClient) -> None:
    payload = {"evening_id": "evening-1", "user_id": "u-1", "dance_role": "follower"}

    response = client.post("/registrations", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["evening_id"] == "evening-1"
    assert body["user_id"] == "u-1"
    assert body["dance_role"] == "follower"
    assert body["status"] == "active"
    assert body["id"]


def test_duplicate_registration_is_rejected(client: TestClient) -> None:
    payload = {"evening_id": "evening-1", "user_id": "u-2", "dance_role": "leader"}

    client.post("/registrations", json=payload)

    response = client.post("/registrations", json=payload)

    assert response.status_code == 409


def test_capacity_is_enforced(client: TestClient) -> None:
    """evening-4 has capacity of exactly one seat: the boundary of AC-04.3."""
    first = client.post(
        "/registrations",
        json={"evening_id": "evening-4", "user_id": "u-3", "dance_role": "follower"},
    )
    second = client.post(
        "/registrations", json={"evening_id": "evening-4", "user_id": "u-4", "dance_role": "leader"}
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_dance_role_is_required(client: TestClient) -> None:
    payload = {"evening_id": "evening-1", "user_id": "u-5"}

    response = client.post("/registrations", json=payload)

    assert response.status_code == 422


def test_role_is_rejected_for_non_dance_evening(client: TestClient) -> None:
    payload = {"evening_id": "evening-2", "user_id": "u-6", "dance_role": "leader"}

    response = client.post("/registrations", json=payload)

    assert response.status_code == 422


def test_started_evening_rejects_registration(client: TestClient) -> None:
    payload = {"evening_id": "evening-3", "user_id": "u-7", "dance_role": "follower"}

    response = client.post("/registrations", json=payload)

    assert response.status_code == 409


def test_unknown_evening_is_rejected(client: TestClient) -> None:
    payload = {"evening_id": "nope", "user_id": "u-8", "dance_role": "follower"}

    response = client.post("/registrations", json=payload)

    assert response.status_code == 404
