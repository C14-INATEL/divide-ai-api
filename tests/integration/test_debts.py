"""Integration tests for the /debts endpoints.

Each endpoint is exercised through the real FastAPI app (routers + auth +
serialization + exception handlers) against an in-memory SQLite database,
covering one happy path and at least one sad path.
"""

import uuid
from types import SimpleNamespace

import pytest

from app.config import settings
from app.repositories.group_repository import GroupRepository

from tests.integration.conftest import auth_headers, make_user


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _debt_payload(world, **overrides) -> dict:
    payload = {
        "group_id": str(world.group.id),
        "title": "Jantar",
        "total_amount": 100,
        "split_type": "homogenea",
        "participants": [
            {"user_id": str(world.creator.id)},
            {"user_id": str(world.member.id)},
        ],
    }
    payload.update(overrides)
    return payload


def _create_debt(client, world) -> dict:
    resp = client.post("/debts/", json=_debt_payload(world), headers=auth_headers(world.creator))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _upload_proof(client, world, user) -> dict:
    files = {"file": ("proof.jpg", b"fake-image-bytes", "image/jpeg")}
    return client.post(
        f"/debts/{world.debt_id}/participants/me/proof",
        files=files,
        headers=auth_headers(user),
    )


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def world(db_session):
    """A group with a creator + member, plus an outsider not in the group."""
    creator = make_user(db_session, "creator@example.com")
    member = make_user(db_session, "member@example.com")
    outsider = make_user(db_session, "outsider@example.com")

    repo = GroupRepository(db_session)
    group = repo.create(name="Trip", creator_id=creator.id)
    repo.add_member(group_id=group.id, user_id=creator.id)
    repo.add_member(group_id=group.id, user_id=member.id)
    db_session.commit()

    return SimpleNamespace(
        db=db_session, creator=creator, member=member, outsider=outsider, group=group
    )


@pytest.fixture
def world_with_debt(client, world):
    """``world`` plus a freshly created debt (all participants pending)."""
    debt = _create_debt(client, world)
    world.debt_id = debt["id"]
    return world


@pytest.fixture(autouse=True)
def _local_storage(monkeypatch, tmp_path):
    """Force the local filesystem storage backend into a temp dir."""
    monkeypatch.setattr(settings, "R2_ENDPOINT_URL", "")
    monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", str(tmp_path))


# --------------------------------------------------------------------------- #
# POST /debts/  (create)
# --------------------------------------------------------------------------- #
class TestCreateDebt:
    def test_creator_creates_debt(self, client, world):
        resp = client.post("/debts/", json=_debt_payload(world), headers=auth_headers(world.creator))

        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Jantar"
        assert body["creator_id"] == str(world.creator.id)
        assert len(body["participants"]) == 2

    def test_non_member_cannot_create(self, client, world):
        resp = client.post("/debts/", json=_debt_payload(world), headers=auth_headers(world.outsider))
        assert resp.status_code == 403

    def test_requires_authentication(self, client, world):
        resp = client.post("/debts/", json=_debt_payload(world))
        assert resp.status_code in (401, 403)  # rejected without credentials


# --------------------------------------------------------------------------- #
# GET /debts/  (list by group)
# --------------------------------------------------------------------------- #
class TestListDebts:
    def test_member_lists_group_debts(self, client, world_with_debt):
        resp = client.get(
            "/debts/",
            params={"group_id": str(world_with_debt.group.id)},
            headers=auth_headers(world_with_debt.member),
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_non_member_cannot_list(self, client, world_with_debt):
        resp = client.get(
            "/debts/",
            params={"group_id": str(world_with_debt.group.id)},
            headers=auth_headers(world_with_debt.outsider),
        )
        assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# GET /debts/{id}  (retrieve)
# --------------------------------------------------------------------------- #
class TestGetDebt:
    def test_member_gets_debt(self, client, world_with_debt):
        resp = client.get(
            f"/debts/{world_with_debt.debt_id}",
            headers=auth_headers(world_with_debt.member),
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == world_with_debt.debt_id

    def test_unknown_debt_returns_404(self, client, world):
        resp = client.get(f"/debts/{uuid.uuid4()}", headers=auth_headers(world.creator))
        assert resp.status_code == 404


# --------------------------------------------------------------------------- #
# PATCH /debts/{id}  (update)
# --------------------------------------------------------------------------- #
class TestUpdateDebt:
    def test_creator_updates_title(self, client, world_with_debt):
        resp = client.patch(
            f"/debts/{world_with_debt.debt_id}",
            json={"title": "Novo título"},
            headers=auth_headers(world_with_debt.creator),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Novo título"

    def test_non_creator_cannot_update(self, client, world_with_debt):
        resp = client.patch(
            f"/debts/{world_with_debt.debt_id}",
            json={"title": "Hack"},
            headers=auth_headers(world_with_debt.member),
        )
        assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# DELETE /debts/{id}
# --------------------------------------------------------------------------- #
class TestDeleteDebt:
    def test_creator_deletes_pending_debt(self, client, world_with_debt):
        resp = client.delete(
            f"/debts/{world_with_debt.debt_id}",
            headers=auth_headers(world_with_debt.creator),
        )
        assert resp.status_code == 204

        # gone afterwards
        follow = client.get(
            f"/debts/{world_with_debt.debt_id}",
            headers=auth_headers(world_with_debt.creator),
        )
        assert follow.status_code == 404

    def test_non_creator_cannot_delete(self, client, world_with_debt):
        resp = client.delete(
            f"/debts/{world_with_debt.debt_id}",
            headers=auth_headers(world_with_debt.member),
        )
        assert resp.status_code == 403

    def test_cannot_delete_with_sent_payment(self, client, world_with_debt):
        # member sends a proof -> their participant becomes "pago"
        assert _upload_proof(client, world_with_debt, world_with_debt.member).status_code == 201

        resp = client.delete(
            f"/debts/{world_with_debt.debt_id}",
            headers=auth_headers(world_with_debt.creator),
        )
        assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# POST /debts/{id}/participants/me/proof  (upload proof)
# --------------------------------------------------------------------------- #
class TestUploadProof:
    def test_participant_uploads_proof(self, client, world_with_debt):
        resp = _upload_proof(client, world_with_debt, world_with_debt.member)

        assert resp.status_code == 201
        body = resp.json()
        assert body["has_proof"] is True
        assert body["status"] == "pago"

    def test_non_participant_cannot_upload(self, client, world_with_debt):
        resp = _upload_proof(client, world_with_debt, world_with_debt.outsider)
        assert resp.status_code == 403

    def test_invalid_file_type_rejected(self, client, world_with_debt):
        files = {"file": ("proof.txt", b"not allowed", "text/plain")}
        resp = client.post(
            f"/debts/{world_with_debt.debt_id}/participants/me/proof",
            files=files,
            headers=auth_headers(world_with_debt.member),
        )
        assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# POST /debts/{id}/participants/{user_id}/confirm
# --------------------------------------------------------------------------- #
class TestConfirmPayment:
    def test_creator_confirms_paid_participant(self, client, world_with_debt):
        _upload_proof(client, world_with_debt, world_with_debt.member)

        resp = client.post(
            f"/debts/{world_with_debt.debt_id}/participants/{world_with_debt.member.id}/confirm",
            headers=auth_headers(world_with_debt.creator),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmado"

    def test_cannot_confirm_without_proof(self, client, world_with_debt):
        resp = client.post(
            f"/debts/{world_with_debt.debt_id}/participants/{world_with_debt.member.id}/confirm",
            headers=auth_headers(world_with_debt.creator),
        )
        assert resp.status_code == 422

    def test_non_creator_cannot_confirm(self, client, world_with_debt):
        _upload_proof(client, world_with_debt, world_with_debt.member)

        resp = client.post(
            f"/debts/{world_with_debt.debt_id}/participants/{world_with_debt.member.id}/confirm",
            headers=auth_headers(world_with_debt.member),
        )
        assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# GET /debts/{id}/participants/{user_id}/proof
# --------------------------------------------------------------------------- #
class TestGetProof:
    def test_member_downloads_proof(self, client, world_with_debt):
        _upload_proof(client, world_with_debt, world_with_debt.member)

        resp = client.get(
            f"/debts/{world_with_debt.debt_id}/participants/{world_with_debt.member.id}/proof",
            headers=auth_headers(world_with_debt.creator),
        )
        assert resp.status_code == 200
        assert resp.content == b"fake-image-bytes"

    def test_missing_proof_returns_404(self, client, world_with_debt):
        resp = client.get(
            f"/debts/{world_with_debt.debt_id}/participants/{world_with_debt.member.id}/proof",
            headers=auth_headers(world_with_debt.creator),
        )
        assert resp.status_code == 404
