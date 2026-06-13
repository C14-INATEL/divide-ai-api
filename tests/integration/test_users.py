"""Integration tests for the /users endpoints.

Exercised through the real FastAPI app against an in-memory SQLite database,
covering one happy path and at least one sad path per endpoint.
"""

import uuid
from types import SimpleNamespace

import pytest

from tests.integration.conftest import auth_headers, make_user


VALID_PASSWORD = "Password123"


@pytest.fixture
def people(db_session):
    actor = make_user(db_session, "actor@example.com", password=VALID_PASSWORD)
    target = make_user(db_session, "target@example.com", password=VALID_PASSWORD)
    db_session.commit()
    return SimpleNamespace(actor=actor, target=target)


# --------------------------------------------------------------------------- #
# POST /users/  (public registration)
# --------------------------------------------------------------------------- #
class TestCreateUser:
    def test_creates_user(self, client):
        resp = client.post(
            "/users/",
            json={"email": "new@example.com", "name": "New", "password": VALID_PASSWORD},
        )
        assert resp.status_code == 201
        assert resp.json()["email"] == "new@example.com"

    def test_weak_password_rejected(self, client):
        resp = client.post(
            "/users/",
            json={"email": "weak@example.com", "name": "Weak", "password": "abc"},
        )
        assert resp.status_code == 422

    def test_duplicate_email_rejected(self, client, people):
        resp = client.post(
            "/users/",
            json={"email": people.actor.email, "name": "Dup", "password": VALID_PASSWORD},
        )
        assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# GET /users/  (search)
# --------------------------------------------------------------------------- #
class TestSearchUsers:
    def test_search_by_name(self, client, people):
        resp = client.get(
            "/users/", params={"name": "target"}, headers=auth_headers(people.actor)
        )
        assert resp.status_code == 200
        emails = [u["email"] for u in resp.json()]
        assert people.target.email in emails

    def test_requires_authentication(self, client, people):
        resp = client.get("/users/")
        assert resp.status_code in (401, 403)


# --------------------------------------------------------------------------- #
# GET /users/{id}
# --------------------------------------------------------------------------- #
class TestGetUser:
    def test_get_user(self, client, people):
        resp = client.get(
            f"/users/{people.target.id}", headers=auth_headers(people.actor)
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == str(people.target.id)

    def test_unknown_user_returns_404(self, client, people):
        resp = client.get(f"/users/{uuid.uuid4()}", headers=auth_headers(people.actor))
        assert resp.status_code == 404


# --------------------------------------------------------------------------- #
# PATCH /users/{id}
# --------------------------------------------------------------------------- #
class TestUpdateUser:
    def test_update_name(self, client, people):
        resp = client.patch(
            f"/users/{people.actor.id}",
            json={"name": "Renamed"},
            headers=auth_headers(people.actor),
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    def test_blank_name_rejected(self, client, people):
        resp = client.patch(
            f"/users/{people.actor.id}",
            json={"name": "   "},
            headers=auth_headers(people.actor),
        )
        assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# PATCH /users/{id}/password
# --------------------------------------------------------------------------- #
class TestUpdatePassword:
    def test_change_password(self, client, people):
        resp = client.patch(
            f"/users/{people.actor.id}/password",
            json={"old_password": VALID_PASSWORD, "new_password": "NewPassword123"},
            headers=auth_headers(people.actor),
        )
        assert resp.status_code == 200

    def test_wrong_old_password_rejected(self, client, people):
        resp = client.patch(
            f"/users/{people.actor.id}/password",
            json={"old_password": "WrongPass123", "new_password": "NewPassword123"},
            headers=auth_headers(people.actor),
        )
        assert resp.status_code == 400
