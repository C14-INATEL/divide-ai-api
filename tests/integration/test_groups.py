"""Integration tests for the /groups endpoints.

Exercised through the real FastAPI app (routers + auth + serialization +
exception handlers) against an in-memory SQLite database, covering one happy
path and at least one sad path per endpoint.
"""

import uuid
from types import SimpleNamespace

import pytest

from app.repositories.group_repository import GroupRepository

from tests.integration.conftest import auth_headers, make_user


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
@pytest.fixture
def people(db_session):
    """A creator, another registered user, and an outsider."""
    creator = make_user(db_session, "creator@example.com")
    other = make_user(db_session, "other@example.com")
    outsider = make_user(db_session, "outsider@example.com")
    db_session.commit()
    return SimpleNamespace(creator=creator, other=other, outsider=outsider)


def _create_group(client, owner, **overrides) -> dict:
    payload = {"name": "Viagem", "description": "Praia"}
    payload.update(overrides)
    resp = client.post("/groups/", json=payload, headers=auth_headers(owner))
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def group(client, people):
    """A group owned by ``people.creator`` (creator is its only member)."""
    return _create_group(client, people.creator)


# --------------------------------------------------------------------------- #
# POST /groups/
# --------------------------------------------------------------------------- #
class TestCreateGroup:
    def test_user_creates_group(self, client, people):
        resp = client.post(
            "/groups/",
            json={"name": "Viagem", "description": "Praia"},
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Viagem"
        assert body["is_owner"] is True
        # creator is automatically a member
        assert any(m["user_id"] == str(people.creator.id) for m in body["members"])

    def test_create_with_unknown_added_user_returns_404(self, client, people):
        resp = client.post(
            "/groups/",
            json={"name": "Viagem", "added_users": [str(uuid.uuid4())]},
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 404

    def test_blank_name_is_rejected(self, client, people):
        resp = client.post(
            "/groups/", json={"name": "   "}, headers=auth_headers(people.creator)
        )
        assert resp.status_code == 422

    def test_requires_authentication(self, client, people):
        resp = client.post("/groups/", json={"name": "Viagem"})
        assert resp.status_code in (401, 403)


# --------------------------------------------------------------------------- #
# GET /groups/
# --------------------------------------------------------------------------- #
class TestListGroups:
    def test_lists_only_groups_user_belongs_to(self, client, people, group):
        # other user has no groups
        resp = client.get("/groups/", headers=auth_headers(people.other))
        assert resp.status_code == 200
        assert resp.json() == []

        # creator sees their group
        resp = client.get("/groups/", headers=auth_headers(people.creator))
        assert [g["id"] for g in resp.json()] == [group["id"]]


# --------------------------------------------------------------------------- #
# GET /groups/{id}
# --------------------------------------------------------------------------- #
class TestGetGroup:
    def test_member_gets_group(self, client, people, group):
        resp = client.get(f"/groups/{group['id']}", headers=auth_headers(people.creator))
        assert resp.status_code == 200
        assert resp.json()["id"] == group["id"]

    def test_non_member_forbidden(self, client, people, group):
        resp = client.get(f"/groups/{group['id']}", headers=auth_headers(people.outsider))
        assert resp.status_code == 403

    def test_unknown_group_returns_404(self, client, people):
        resp = client.get(f"/groups/{uuid.uuid4()}", headers=auth_headers(people.creator))
        assert resp.status_code == 404


# --------------------------------------------------------------------------- #
# PATCH /groups/{id}
# --------------------------------------------------------------------------- #
class TestUpdateGroup:
    def test_creator_updates_name(self, client, people, group):
        resp = client.patch(
            f"/groups/{group['id']}",
            json={"name": "Novo nome"},
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Novo nome"

    def test_non_creator_cannot_update(self, client, people, group):
        resp = client.patch(
            f"/groups/{group['id']}",
            json={"name": "Hack"},
            headers=auth_headers(people.other),
        )
        assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# DELETE /groups/{id}
# --------------------------------------------------------------------------- #
class TestDeleteGroup:
    def test_creator_deletes_group(self, client, people, group):
        resp = client.delete(f"/groups/{group['id']}", headers=auth_headers(people.creator))
        assert resp.status_code == 204

        follow = client.get(f"/groups/{group['id']}", headers=auth_headers(people.creator))
        assert follow.status_code == 404

    def test_non_creator_cannot_delete(self, client, people, group):
        resp = client.delete(f"/groups/{group['id']}", headers=auth_headers(people.other))
        assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# POST /groups/{id}/members
# --------------------------------------------------------------------------- #
class TestAddMember:
    def test_creator_adds_member(self, client, people, group):
        resp = client.post(
            f"/groups/{group['id']}/members",
            json={"user_id": str(people.other.id)},
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 201
        assert resp.json()["user_id"] == str(people.other.id)

    def test_non_creator_cannot_add(self, client, people, group):
        resp = client.post(
            f"/groups/{group['id']}/members",
            json={"user_id": str(people.outsider.id)},
            headers=auth_headers(people.other),
        )
        assert resp.status_code == 403

    def test_add_unknown_user_returns_404(self, client, people, group):
        resp = client.post(
            f"/groups/{group['id']}/members",
            json={"user_id": str(uuid.uuid4())},
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 404

    def test_add_existing_member_returns_400(self, client, people, group):
        resp = client.post(
            f"/groups/{group['id']}/members",
            json={"user_id": str(people.creator.id)},
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# DELETE /groups/{id}/members/{user_id}
# --------------------------------------------------------------------------- #
class TestRemoveMember:
    def _add(self, client, people, group, user):
        client.post(
            f"/groups/{group['id']}/members",
            json={"user_id": str(user.id)},
            headers=auth_headers(people.creator),
        )

    def test_creator_removes_member(self, client, people, group, db_session):
        self._add(client, people, group, people.other)

        resp = client.delete(
            f"/groups/{group['id']}/members/{people.other.id}",
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 204
        assert GroupRepository(db_session).get_member(
            uuid.UUID(group["id"]), people.other.id
        ) is None

    def test_cannot_remove_creator(self, client, people, group):
        resp = client.delete(
            f"/groups/{group['id']}/members/{people.creator.id}",
            headers=auth_headers(people.creator),
        )
        assert resp.status_code == 400

    def test_non_creator_cannot_remove(self, client, people, group):
        self._add(client, people, group, people.other)

        resp = client.delete(
            f"/groups/{group['id']}/members/{people.other.id}",
            headers=auth_headers(people.other),
        )
        assert resp.status_code == 403
