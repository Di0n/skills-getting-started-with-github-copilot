from fastapi.testclient import TestClient
import pytest

from src.app import app, activities  # the in-memory store is mutated by tests

client = TestClient(app)


def test_get_activities():
    """GET /activities returns the dictionary of activities."""
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data  # one of the seeded activities


def test_signup_and_prevent_duplicates():
    """You can sign up once but not twice for the same activity."""
    email = "tester@mergington.edu"
    activity = "Chess Club"

    # make sure the email isn't already present
    participants = activities[activity]["participants"]
    if email in participants:
        participants.remove(email)

    # first signup succeeds
    resp = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # second signup is rejected with 400
    resp2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )
    assert resp2.status_code == 400
    assert "already signed up" in resp2.json().get("detail", "")


def test_signup_nonexistent_activity():
    resp = client.post(
        "/activities/does-not-exist/signup",
        params={"email": "foo@bar.com"},
    )
    assert resp.status_code == 404


def test_unregister_flow():
    email = "removeme@mergington.edu"
    activity = "Chess Club"

    # ensure the participant is registered first
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    resp = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email},
    )
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]

    # trying again returns 400
    resp2 = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email},
    )
    assert resp2.status_code == 400
    assert "not signed up" in resp2.json().get("detail", "")
