"""Shared fixtures for debt endpoint integration tests.

The TestClient talks to the real (in-memory SQLite) ``db_session`` through a
``get_db`` dependency override. Authentication is *not* overridden: tests send
real JWTs (see ``auth_headers``), so the full ``get_current_user`` ->
``UserRepository`` lookup runs end to end against the same session.
"""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.utils.jwt import create_access_token


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_headers(user) -> dict:
    """Authorization header carrying a valid token for ``user``."""
    token = create_access_token(
        {"sub": str(user.id), "email": user.email, "name": user.name},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}
