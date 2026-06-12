"""Integration tests for the /auth endpoints."""

import pytest

from tests.integration.conftest import make_user


VALID_PASSWORD = "Password123"


@pytest.fixture
def user(db_session):
    u = make_user(db_session, "login@example.com", password=VALID_PASSWORD)
    db_session.commit()
    return u


class TestLogin:
    def test_valid_credentials_return_token(self, client, user):
        resp = client.post(
            "/auth/login", json={"email": user.email, "password": VALID_PASSWORD}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["access_token"]
        assert body["token_type"] == "bearer"

    def test_wrong_password_rejected(self, client, user):
        resp = client.post(
            "/auth/login", json={"email": user.email, "password": "WrongPass123"}
        )
        assert resp.status_code == 400

    def test_unknown_email_rejected(self, client):
        resp = client.post(
            "/auth/login", json={"email": "nobody@example.com", "password": VALID_PASSWORD}
        )
        assert resp.status_code == 400

    def test_malformed_email_returns_422(self, client):
        resp = client.post(
            "/auth/login", json={"email": "not-an-email", "password": VALID_PASSWORD}
        )
        assert resp.status_code == 422
